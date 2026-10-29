// Desktop source-file links use the native save dialog; the accepted viewer is unchanged.
if (!document.documentElement.dataset.flyvisDesktopLinks) {
  document.documentElement.dataset.flyvisDesktopLinks = 'true';
  document.addEventListener('click', event => {
    const link = event.target.closest('a[target="_blank"]');
    if (!link) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || !url.pathname.includes('/files/')) return;
    event.preventDefault();
    const save = document.createElement('a');
    save.href = url.href;
    save.download = url.pathname.split('/').pop();
    document.body.append(save);
    save.click();
    save.remove();
  });
}
