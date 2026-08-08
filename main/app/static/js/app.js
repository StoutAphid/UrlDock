// UrlDock UI enhancements (vanilla JS, complements HTMX/Alpine)

document.addEventListener('htmx:afterRequest', function (event) {
    // Scroll newly-added card into view
    const target = event.detail.target;
    if (event.detail.path === '/_ui/links' && target) {
        const firstCard = target.querySelector('.link-card');
        if (firstCard) {
            firstCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
});

document.addEventListener('htmx:responseError', function (event) {
    let detail = event.detail;
    let node = detail.target;
    let message = node && node.querySelector('.error-state');
    if (message) {
        message.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});