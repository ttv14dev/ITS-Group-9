// Giao diện nhận diện phương tiện ưu tiên: chọn ảnh/video, gọi API, hiển thị kết quả.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);

  const MAX_IMAGE = 10 * 1024 * 1024;
  const MAX_VIDEO = 50 * 1024 * 1024;
  const IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];
  const VIDEO_EXT = [".mp4", ".avi", ".mov", ".mkv", ".webm"];

  const input = $("file-input");
  const dropArea = $("drop-area");
  let file = null;      // file đang chọn
  let kind = null;      // "image" | "video"
  let previewUrl = null;

  const fmtMB = (n) => (n / 1024 / 1024).toFixed(1) + " MB";
  const show = (el, on) => { el.hidden = !on; };
  const extOf = (name) => (name.lastIndexOf(".") >= 0 ? name.slice(name.lastIndexOf(".")).toLowerCase() : "");

  function setFileError(msg) {
    $("file-error").textContent = msg || "";
    show($("file-error"), !!msg);
  }

  function resetResult() {
    show($("result"), false);
    show($("result-error"), false);
    show($("result-loading"), false);
    show($("result-empty"), true);
  }

  function clearFile() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null; file = null; kind = null;
    input.value = "";
    $("preview").replaceChildren();
    show($("preview"), false);
    show($("drop-empty"), true);
    show($("file-info"), false);
    setFileError("");
    $("btn-detect").disabled = true;
    $("btn-clear").disabled = true;
    resetResult();
  }

  function pickFile(f) {
    setFileError("");
    if (!f) return;
    const isImage = IMAGE_TYPES.includes(f.type);
    const isVideo = f.type.startsWith("video/") || VIDEO_EXT.includes(extOf(f.name));
    if (!isImage && !isVideo) {
      setFileError("File không được hỗ trợ. Hãy chọn ảnh JPG, PNG, WEBP hoặc video MP4, AVI, MOV, MKV, WEBM.");
      return;
    }
    if (isImage && f.size > MAX_IMAGE) { setFileError("Ảnh quá lớn (" + fmtMB(f.size) + "), tối đa 10 MB."); return; }
    if (isVideo && !isImage && f.size > MAX_VIDEO) { setFileError("Video quá lớn (" + fmtMB(f.size) + "), tối đa 50 MB."); return; }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    file = f;
    kind = isImage ? "image" : "video";
    previewUrl = URL.createObjectURL(f);

    const el = document.createElement(kind === "image" ? "img" : "video");
    el.src = previewUrl;
    if (kind === "image") el.alt = "Ảnh đã chọn";
    else { el.controls = true; el.muted = true; el.preload = "metadata"; el.addEventListener("click", (e) => e.preventDefault()); }
    $("preview").replaceChildren(el);
    show($("preview"), true);
    show($("drop-empty"), false);

    $("file-info").textContent = (kind === "image" ? "Ảnh: " : "Video: ") + f.name + " (" + fmtMB(f.size) + ")";
    show($("file-info"), true);
    $("btn-detect").disabled = false;
    $("btn-clear").disabled = false;
    resetResult();
  }

  input.addEventListener("change", () => pickFile(input.files[0]));
  $("btn-clear").addEventListener("click", clearFile);
  ["dragenter", "dragover"].forEach((ev) => dropArea.addEventListener(ev, (e) => { e.preventDefault(); dropArea.classList.add("is-over"); }));
  ["dragleave", "drop"].forEach((ev) => dropArea.addEventListener(ev, (e) => { e.preventDefault(); dropArea.classList.remove("is-over"); }));
  dropArea.addEventListener("drop", (e) => pickFile(e.dataTransfer.files[0]));

  // ---------- Hiển thị kết quả ----------
  function setLoading(on, text) {
    show($("result-loading"), on);
    if (text) $("loading-text").textContent = text;
    if (on) { show($("result-empty"), false); show($("result"), false); show($("result-error"), false); }
    $("btn-detect").disabled = on || !file;
  }

  function showError(msg) {
    show($("result-empty"), false);
    show($("result"), false);
    $("result-error").textContent = msg;
    show($("result-error"), true);
  }

  function render(data) {
    show($("result-empty"), false);
    show($("result-error"), false);

    const banner = $("banner");
    if (data.is_priority) { banner.className = "banner banner--priority"; banner.textContent = "PHƯƠNG TIỆN ƯU TIÊN: " + data.label_vi; }
    else { banner.className = "banner banner--none"; banner.textContent = data.label_vi || "Không phát hiện xe ưu tiên"; }

    $("result-message").textContent = data.message || "";
    $("r-type").textContent = data.vehicle_type ? data.label_vi : "-";

    const hasScore = data.confidence !== null && data.confidence !== undefined;
    $("r-score-label").textContent = "Độ tin cậy của mô hình";
    $("r-score").textContent = hasScore ? Math.round(data.confidence * 100) + "%" : "Không có";

    // Video: dòng thời gian
    const v = data.video;
    show($("r-video-row"), !!v);
    show($("timeline-box"), !!v);
    if (v) {
      $("r-video").textContent = v.frames_analyzed + " khung (video dài " + v.duration_s + " giây), " + v.priority_frames + " khung có xe ưu tiên";
      const tl = $("timeline");
      tl.replaceChildren();
      v.timeline.forEach((f) => {
        const t = document.createElement("span");
        t.className = "tick " + (f.is_priority ? "tick--red" : "");
        t.title = f.time_s + " giây: " + (f.is_priority ? "có xe ưu tiên" : "không thấy xe ưu tiên");
        tl.appendChild(t);
      });
    }

    // Ảnh đã đánh dấu
    const hasImg = !!data.annotated_image;
    show($("annotated-box"), hasImg);
    if (hasImg) {
      $("annotated").src = data.annotated_image;
      $("annotated-caption").textContent = (v ? "Khung hình tiêu biểu của video. " : "") + "Khung đỏ: xe ưu tiên do mô hình phát hiện.";
    }

    // Danh sách xe
    const list = $("det-list");
    list.replaceChildren();
    const dets = data.detections || [];
    show($("det-box"), dets.length > 0);
    dets.forEach((d) => {
      const li = document.createElement("li");
      const num = document.createElement("span");
      num.className = "num" + (d.is_priority ? " num--priority" : "");
      num.textContent = d.index;
      const body = document.createElement("div");
      const name = document.createElement("span");
      name.className = "name";
      name.textContent = d.label_vi + (d.is_priority ? " (ưu tiên)" : "");
      const meta = document.createElement("div");
      meta.className = "meta";
      meta.textContent = "Độ tin cậy " + Math.round(d.score * 100) + "%";
      body.append(name, meta);
      li.append(num, body);
      list.appendChild(li);
    });

    show($("result"), true);
  }

  async function post(url, options, loadingText) {
    setLoading(true, loadingText);
    try {
      const res = await fetch(url, options);
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = typeof body.detail === "string" ? body.detail : "Yêu cầu không hợp lệ (mã " + res.status + ").";
        throw new Error(detail);
      }
      render(body);
    } catch (err) {
      showError(err instanceof TypeError
        ? "Không kết nối được máy chủ. Hãy chạy backend (uvicorn backend.main:app) rồi mở lại trang."
        : err.message);
    } finally {
      setLoading(false);
    }
  }

  $("btn-detect").addEventListener("click", () => {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    post(kind === "image" ? "/api/detect/image" : "/api/detect/video", { method: "POST", body: form },
      kind === "image" ? "Đang phân tích ảnh..." : "Đang phân tích video, có thể mất vài giây...");
  });
})();
