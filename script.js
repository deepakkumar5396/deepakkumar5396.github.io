const yearNode = document.getElementById("year");

if (yearNode) {
  yearNode.textContent = new Date().getFullYear();
}

const formatCounter = (element, value) => {
  const prefix = element.dataset.prefix || "";
  const suffix = element.dataset.suffix || "";
  const decimals = Number(element.dataset.decimals || 0);

  return `${prefix}${value.toFixed(decimals)}${suffix}`;
};

const animateCounter = (element) => {
  if (element.dataset.animated === "true") {
    return;
  }

  const target = Number(element.dataset.number || 0);
  const duration = 1400;
  const start = performance.now();

  element.dataset.animated = "true";

  const tick = (now) => {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = target * eased;

    element.textContent = formatCounter(element, current);

    if (progress < 1) {
      requestAnimationFrame(tick);
      return;
    }

    element.textContent = formatCounter(element, target);
  };

  requestAnimationFrame(tick);
};

const revealTargets = document.querySelectorAll("[data-reveal]");
const metricTargets = document.querySelectorAll(".metric-value[data-number]");

metricTargets.forEach((node) => {
  node.textContent = formatCounter(node, 0);
});

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) {
        return;
      }

      entry.target.classList.add("is-visible");

      if (entry.target.classList.contains("metric-value")) {
        animateCounter(entry.target);
      }

      observer.unobserve(entry.target);
    });
  },
  {
    threshold: 0.2,
    rootMargin: "0px 0px -10% 0px"
  }
);

revealTargets.forEach((node) => observer.observe(node));
metricTargets.forEach((node) => observer.observe(node));
