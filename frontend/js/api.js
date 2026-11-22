// Gọi API backend và hiển thị kết quả nhận diện
(function () {
  const $ = (id) => document.getElementById(id);
  const result = $("result");
  const statusEl = $("result-status");
  const loadingEl = $("result-loading");
  const errorEl = $("result-error");
  const typeEl = $("result-type");
  const confEl = $("result-confidence");
  const meterEl = $("result-meter");
  const typeError = $("type-error");
  let alerts = 0;

  function setLoading(on) {
    loadingEl.hidden = !on;
    $("btn-start").disabled = on;
    $("type-submit").disabled = on;
  }

  function showError(message) {
    result.dataset.state = "error";
    statusEl.textContent = "Có lỗi";
    errorEl.textContent = message;
    errorEl.hidden = false;
    typeEl.textContent = "—";
    confEl.textContent = "—";
    meterEl.style.width = "0";
  }

  function showResult(data, source, ms) {
    errorEl.hidden = true;
    result.dataset.state = data.is_priority ? "priority" : "normal";
    statusEl.textContent = data.is_priority ? "PHƯƠNG TIỆN ƯU TIÊN" : "Xe thường";
    typeEl.textContent = data.label_vi;
    // Chọn từ danh sách thì không có độ tin cậy
    const pct = data.confidence == null ? null : Math.round(data.confidence * 100);
    confEl.textContent = pct == null ? "Không áp dụng (chọn từ danh sách)" : pct + "%";
    meterEl.style.width = (pct == null ? 100 : pct) + "%";
    $("stage-source").textContent = source;
    $("stat-source").textContent = source;
    $("stat-latency").textContent = ms + " ms";
    $("stat-objects").textContent = "1";
    if (data.is_priority) {
      alerts += 1;
      $("stat-alerts").textContent = String(alerts);
    }
  }

  async function call(url, options, source) {
    errorEl.hidden = true;
    typeError.hidden = true;
    setLoading(true);
    const start = performance.now();
    try {
      const res = await fetch(url, options);
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = typeof body.detail === "string" ? body.detail : "Yêu cầu không hợp lệ.";
        throw new Error(detail);
      }
      showResult(body, source, Math.round(performance.now() - start));
    } catch (err) {
      const offline = err instanceof TypeError;
      showError(offline ? "Không kết nối được máy chủ. Hãy chạy backend rồi mở lại trang." : err.message);
    } finally {
      setLoading(false);
    }
  }

  // Nhận diện theo loại xe
  $("type-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const chosen = document.querySelector('input[name="vehicle_type"]:checked');
    if (!chosen) {
      typeError.textContent = "Vui lòng chọn một loại xe.";
      typeError.hidden = false;
      return;
    }
    call("/api/detect/type", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vehicle_type: chosen.value }),
    }, "Danh sách");
  });

  // Nhận diện theo ảnh đã tải lên
  $("btn-start").addEventListener("click", function () {
    const file = window.selectedFile;
    if (!file) {
      showError("Hãy tải ảnh lên trước khi nhận diện.");
      return;
    }
    const form = new FormData();
    form.append("file", file);
    call("/api/detect/image", { method: "POST", body: form }, "Ảnh tải lên");
  });

  // Đặt lại
  $("btn-reset").addEventListener("click", function () {
    $("clearButton").click();
    $("type-form").reset();
    result.dataset.state = "empty";
    statusEl.textContent = "Sẵn sàng";
    errorEl.hidden = true;
    typeError.hidden = true;
    typeEl.textContent = "—";
    confEl.textContent = "—";
    meterEl.style.width = "0";
    $("stage-source").textContent = "Chưa có";
    $("stat-source").textContent = "Chưa có";
    $("stat-latency").textContent = "– ms";
    $("stat-objects").textContent = "0";
  });
})();
