(function () {
  const modal = document.getElementById('loginModal');
  if (!modal) return;
  const closeBtn = document.getElementById('modalCloseBtn');
  const loginBtn = document.getElementById('modalLoginBtn');
  const protectedLinks = document.querySelectorAll('[data-protected-action]');
  protectedLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      const isAuthenticated = link.dataset.isAuthenticated === 'true';
      if (isAuthenticated) return;
      event.preventDefault();
      loginBtn.href = '/users/login/?next=' + encodeURIComponent(link.getAttribute('href'));
      modal.classList.remove('hidden');
    });
  });
  closeBtn?.addEventListener('click', () => modal.classList.add('hidden'));
  modal.addEventListener('click', (event) => {
    if (event.target === modal) modal.classList.add('hidden');
  });
})();
