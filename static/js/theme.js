document.addEventListener('DOMContentLoaded', function() {
  const themeToggle = document.getElementById('theme-toggle');
  const currentTheme = localStorage.getItem('theme') || 'light';
  
  // Set initial theme
  if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeToggle.checked = true;
  }
  
  // Handle theme toggle
  themeToggle.addEventListener('change', function() {
    if (this.checked) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
  });

  // Theme mode buttons
  const lightModeBtn = document.querySelector('.light-mode-btn');
  const darkModeBtn = document.querySelector('.dark-mode-btn');
  
  if (lightModeBtn && darkModeBtn) {
      // Light mode button click
      lightModeBtn.addEventListener('click', function() {
          if (window.themeSwitcher) {
              window.themeSwitcher.setThemeMode('manual');
              window.themeSwitcher.setLightTheme();
          }
      });
      
      // Dark mode button click
      darkModeBtn.addEventListener('click', function() {
          if (window.themeSwitcher) {
              window.themeSwitcher.setThemeMode('manual');
              window.themeSwitcher.setDarkTheme();
          }
      });
      
      // Update active button state when theme changes
      document.addEventListener('themeChanged', function(e) {
          if (e.detail === 'dark') {
              darkModeBtn.classList.add('active');
              lightModeBtn.classList.remove('active');
          } else {
              lightModeBtn.classList.add('active');
              darkModeBtn.classList.remove('active');
          }
      });
      
      // Set initial active state
      if (document.body.classList.contains('dark-theme')) {
          darkModeBtn.classList.add('active');
      } else {
          lightModeBtn.classList.add('active');
      }
  }
});
