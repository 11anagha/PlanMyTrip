document.addEventListener("DOMContentLoaded", function () {
  const sections = document.querySelectorAll(".about_box, .package, .faq");

  const revealSection = (entries, observer) => {
      entries.forEach(entry => {
          if (entry.isIntersecting) {
              entry.target.style.opacity = "1";
              entry.target.style.filter = "none";
              entry.target.style.transform = "none";
              observer.unobserve(entry.target);
          }
      });
  };

  const observer = new IntersectionObserver(revealSection, {
      threshold: 0.2,
  });

  sections.forEach(section => {
      observer.observe(section);
  });
});
