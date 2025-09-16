// Native JavaScript implementation of jQuery shorten plugin
window.TextShortener = {
    config: {
        showChars: 100,
        ellipsesText: "...",
        moreText: "Ver mais",
        lessText: "Ver menos"
    },

    init: function(settings) {
        if (settings) {
            Object.assign(this.config, settings);
        }
        
        // Remove existing event listeners
        document.removeEventListener("click", this.handleClick);
        
        // Add new event listener
        document.addEventListener("click", this.handleClick.bind(this));
    },

    handleClick: function(event) {
        if (event.target.classList.contains('morelink')) {
            event.preventDefault();
            
            const link = event.target;
            const moreContent = link.closest('.morecontent');
            const moreEllipses = moreContent.previousElementSibling;
            
            if (link.classList.contains('less')) {
                link.classList.remove('less');
                link.textContent = this.config.moreText;
                moreEllipses.style.display = 'inline';
                moreContent.querySelector('span').style.display = 'none';
            } else {
                link.classList.add('less');
                link.textContent = this.config.lessText;
                moreEllipses.style.display = 'none';
                moreContent.querySelector('span').style.display = 'inline';
            }
        }
    },

    shorten: function(element, settings) {
        const config = Object.assign({}, this.config);
        if (settings) {
            Object.assign(config, settings);
        }
        
        if (element.classList.contains("shortened")) return;
        
        element.classList.add("shortened");
        const content = element.innerHTML;
        
        if (content.length > config.showChars) {
            const c = content.substr(0, config.showChars);
            const h = content.substr(config.showChars, content.length - config.showChars);
            const html = c + '<span class="moreellipses">' + config.ellipsesText + ' </span><span class="morecontent"><span style="display: none;">' + h + '</span> <a href="#" class="morelink">' + config.moreText + '</a></span>';
            element.innerHTML = html;
        }
    }
};

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    TextShortener.init();
});

// Helper function to shorten text (similar to jQuery usage)
window.shortenText = function(selector, settings) {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
        TextShortener.shorten(element, settings);
    });
};