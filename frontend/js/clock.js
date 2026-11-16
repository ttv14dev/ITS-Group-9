// Đồng hồ ở góc phải thanh tiêu đề
(function () {
  const timeEl = document.getElementById("clock");
  const dateEl = document.getElementById("clock-date");
  if (!timeEl || !dateEl) return;

  const pad = (n) => String(n).padStart(2, "0");

  function tick() {
    const d = new Date();
    timeEl.textContent = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    dateEl.textContent = `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
  }

  tick();
  setInterval(tick, 1000);
})();