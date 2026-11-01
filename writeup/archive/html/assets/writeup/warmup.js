(function () {
  "use strict";

  const figure = document.getElementById("warmup");
  if (!figure) return;

  const registers = { a: 255, b: 241 };
  const inputs = [...figure.querySelectorAll("[data-value]")];
  const bits = [...figure.querySelectorAll("[data-bit]")];
  const error = figure.querySelector("#warmup-error");
  const result = figure.querySelector(".warmup-result");

  function render() {
    for (const input of inputs) {
      input.value = registers[input.dataset.value];
      input.removeAttribute("aria-invalid");
    }
    for (const button of bits) {
      const value = (registers[button.dataset.register] >> Number(button.dataset.bit)) & 1;
      button.setAttribute("aria-pressed", String(value === 1));
      button.querySelector("strong").textContent = value;
    }
    for (const name of ["a", "b"]) {
      const value = registers[name];
      figure.querySelector('[data-literals="' + name + '"]').textContent =
        Array.from({ length: 8 }, (_, bit) =>
          ((value >> bit) & 1 ? "" : "¬") + name.toUpperCase() + bit
        ).join(" ∧ ");
    }
    const sum = registers.a + registers.b;
    const success = sum === 496;
    figure.querySelector("[data-sum]").textContent =
      registers.a + " + " + registers.b + " = " + sum;
    result.dataset.success = String(success);
    figure.querySelector("[data-status]").textContent = success
      ? "success = 1"
      : "success = 0";
    error.hidden = true;
    error.textContent = "";
  }

  for (const input of inputs) {
    input.addEventListener("input", function () {
      const value = input.valueAsNumber;
      if (!Number.isInteger(value) || value < 0 || value > 255) {
        input.setAttribute("aria-invalid", "true");
        error.textContent = "Enter a whole number from 0 to 255. The figure still shows the last valid registers.";
        error.hidden = false;
        return;
      }
      registers[input.dataset.value] = value;
      render();
    });
  }
  for (const button of bits) {
    button.addEventListener("click", function () {
      registers[button.dataset.register] ^= 1 << Number(button.dataset.bit);
      render();
    });
  }
  for (const button of figure.querySelectorAll("[data-example]")) {
    button.addEventListener("click", function () {
      registers.a = 255;
      registers.b = button.dataset.example === "success" ? 241 : 240;
      render();
    });
  }

  render();
  for (const control of [...inputs, ...bits]) control.disabled = false;
  figure.querySelector(".warmup-examples").hidden = false;
})();
