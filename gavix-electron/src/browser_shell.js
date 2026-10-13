// Browser shell UI logic connecting omnibox, tabs, and webview to GAVIX Search
document.addEventListener('DOMContentLoaded', () => {
  const omnibox = document.getElementById('omnibox-input');
  const btnBack = document.getElementById('btn-back');
  const btnForward = document.getElementById('btn-forward');
  const btnReload = document.getElementById('btn-reload');
  const addTabBtn = document.getElementById('add-tab-btn');
  const newtabFrame = document.getElementById('newtab-frame');
  const activeWebview = document.getElementById('active-webview');
  const tabsContainer = document.getElementById('tabs-container');

  const searchBaseUrl = 'http://127.0.0.1:8000';

  function navigateTo(target) {
    if (!target) return;
    const url = target.trim();

    // Check if it's a URL or a search query
    let destination;
    if (url.startsWith('http://') || url.startsWith('https://')) {
      destination = url;
    } else if (url.includes('.') && !url.includes(' ')) {
      destination = 'https://' + url;
    } else {
      // GAVIX Search query
      destination = `${searchBaseUrl}/search?q=${encodeURIComponent(url)}`;
    }

    // Switch from new tab frame to active webview
    newtabFrame.classList.add('hidden');
    activeWebview.classList.remove('hidden');
    activeWebview.src = destination;
    omnibox.value = destination;
  }

  // Omnibox Enter trigger
  omnibox.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      navigateTo(omnibox.value);
    }
  });

  // Navigation button controls
  btnBack.addEventListener('click', () => {
    if (!activeWebview.classList.contains('hidden') && activeWebview.canGoBack()) {
      activeWebview.goBack();
    }
  });

  btnForward.addEventListener('click', () => {
    if (!activeWebview.classList.contains('hidden') && activeWebview.canGoForward()) {
      activeWebview.goForward();
    }
  });

  btnReload.addEventListener('click', () => {
    if (!activeWebview.classList.contains('hidden')) {
      activeWebview.reload();
    } else {
      newtabFrame.src = newtabFrame.src;
    }
  });

  // Home sidebar button
  document.getElementById('side-home').addEventListener('click', () => {
    activeWebview.classList.add('hidden');
    newtabFrame.classList.remove('hidden');
    omnibox.value = '';
    omnibox.placeholder = 'Search GAVIX or type a URL';
  });

  // Listen for navigation messages from newtab-frame (when user clicks shortcuts or searches)
  window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'GAVIX_NAVIGATE') {
      navigateTo(event.data.url);
    }
  });

  // Webview events to update Omnibox URL
  activeWebview.addEventListener('did-navigate', (e) => {
    omnibox.value = e.url;
    const activeTab = document.querySelector('.tab.active .tab-title');
    if (activeTab) activeTab.textContent = activeWebview.getTitle() || e.url;
  });

  activeWebview.addEventListener('page-title-updated', (e) => {
    const activeTab = document.querySelector('.tab.active .tab-title');
    if (activeTab) activeTab.textContent = e.title;
  });

  // New Tab button
  addTabBtn.addEventListener('click', () => {
    activeWebview.classList.add('hidden');
    newtabFrame.classList.remove('hidden');
    omnibox.value = '';
    omnibox.placeholder = 'Search GAVIX or type a URL';
  });
});
