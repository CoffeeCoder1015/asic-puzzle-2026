(() => {
  const candidateExplorer = document.querySelector('#candidate-explorer');
  const candidateButtons = [...candidateExplorer.querySelectorAll('[data-byte]')];
  const candidatePanels = [...candidateExplorer.querySelectorAll('[data-candidate]')];

  function chooseCandidate(byte, announce) {
    candidateExplorer.querySelector('.requested-prefix').textContent = `T${byte}`;
    candidateButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.byte === byte)));
    candidatePanels.forEach(panel => {
      panel.hidden = panel.dataset.candidate !== byte;
      if (announce && !panel.hidden) {
        const answer = panel.querySelector('.candidate-answer');
        candidateExplorer.querySelector('.candidate-status').textContent = `${answer.querySelector('code').textContent}, ${answer.querySelector('.status').textContent}`;
        if (window.gsap && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          gsap.fromTo(panel, { opacity: 0.4, y: 4 }, { opacity: 1, y: 0, duration: 0.25, clearProps: 'all', overwrite: true });
        }
      }
    });
  }

  candidateButtons.forEach(button => button.addEventListener('click', () => chooseCandidate(button.dataset.byte, true)));
  chooseCandidate('R', false);
  candidateExplorer.querySelector('.candidate-controls').hidden = false;

  const enumeration = document.querySelector('#prefix-enumeration');
  const steps = [...enumeration.querySelectorAll('.enumeration-steps > li')];
  const controls = enumeration.querySelector('.enumeration-controls');
  const previous = controls.querySelector('[data-action="previous"]');
  const next = controls.querySelector('[data-action="next"]');
  const replay = controls.querySelector('[data-action="reset"]');
  const status = controls.querySelector('.enumeration-status');
  let currentStep = 0;

  function showStep(index) {
    currentStep = index;
    steps.forEach((step, stepIndex) => {
      step.hidden = stepIndex !== currentStep;
    });
    previous.disabled = currentStep === 0;
    next.disabled = currentStep === steps.length - 1;
    next.textContent = steps[currentStep].dataset.nextLabel;
    replay.hidden = currentStep !== steps.length - 1;
    status.textContent = `Query ${currentStep + 1} of ${steps.length}`;
  }

  previous.addEventListener('click', () => showStep(currentStep - 1));
  next.addEventListener('click', () => showStep(currentStep + 1));
  replay.addEventListener('click', () => {
    showStep(0);
    next.focus();
  });
  showStep(0);
  controls.hidden = false;
  enumeration.classList.add('is-interactive');

  if (window.gsap) {
    gsap.matchMedia().add('(prefers-reduced-motion: no-preference)', context => {
      const observer = new IntersectionObserver(entries => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          context.add(() => gsap.from(entry.target, {
            opacity: 0.35,
            y: 12,
            duration: 0.65,
            ease: 'power2.out',
            clearProps: 'all',
          }));
          observer.unobserve(entry.target);
        }
      }, { threshold: 0.12 });
      document.querySelectorAll('.explanation, .extraction-stages, .board-result').forEach(figure => observer.observe(figure));
      return () => observer.disconnect();
    });
  }
})();
