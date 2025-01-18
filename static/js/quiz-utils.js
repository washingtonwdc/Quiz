class QuizThemeManager {
    constructor() {
        this.themes = {
            light: {
                '--bg-primary': '#ffffff',
                '--bg-secondary': '#f8f9fa',
                '--text-primary': '#212529',
                '--accent-color': '#0d6efd'
            },
            dark: {
                '--bg-primary': '#1a1a1a',
                '--bg-secondary': '#2d2d2d',
                '--text-primary': '#ffffff',
                '--accent-color': '#3d8bfd'
            },
            sepia: {
                '--bg-primary': '#f4e4bc',
                '--bg-secondary': '#eadec2',
                '--text-primary': '#5c4b37',
                '--accent-color': '#8b6b4f'
            }
        };
        this.currentTheme = localStorage.getItem('quiz-theme') || 'light';
        this.applyTheme(this.currentTheme);
    }

    applyTheme(themeName) {
        const theme = this.themes[themeName];
        Object.entries(theme).forEach(([property, value]) => {
            document.documentElement.style.setProperty(property, value);
        });
        localStorage.setItem('quiz-theme', themeName);
    }
}

class QuizSoundManager {
    constructor() {
        this.sounds = {
            click: new Audio('/static/sounds/click.mp3'),
            correct: new Audio('/static/sounds/correct.mp3'),
            incorrect: new Audio('/static/sounds/incorrect.mp3'),
            timer: new Audio('/static/sounds/timer.mp3'),
            complete: new Audio('/static/sounds/complete.mp3')
        };
        this.enabled = JSON.parse(localStorage.getItem('quiz-sound-enabled') || 'true');
    }

    play(soundName) {
        if (this.enabled && this.sounds[soundName]) {
            this.sounds[soundName].play();
        }
    }

    toggle() {
        this.enabled = !this.enabled;
        localStorage.setItem('quiz-sound-enabled', this.enabled);
    }
}

class QuizGestureManager {
    constructor(element) {
        this.element = element;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.minSwipeDistance = 50;
        this.maxSwipeTime = 300;
        this.touchStartTime = 0;
        this.initListeners();
    }

    initListeners() {
        this.element.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
            this.touchStartY = e.changedTouches[0].screenY;
            this.touchStartTime = Date.now();
        });

        this.element.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.touchEndY = e.changedTouches[0].screenY;
            this.handleGesture();
        });
    }

    handleGesture() {
        const touchTime = Date.now() - this.touchStartTime;
        const deltaX = this.touchEndX - this.touchStartX;
        const deltaY = this.touchEndY - this.touchStartY;

        if (touchTime > this.maxSwipeTime) return;

        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            if (Math.abs(deltaX) > this.minSwipeDistance) {
                if (deltaX > 0) {
                    this.onSwipeRight();
                } else {
                    this.onSwipeLeft();
                }
            }
        } else {
            if (Math.abs(deltaY) > this.minSwipeDistance) {
                if (deltaY > 0) {
                    this.onSwipeDown();
                } else {
                    this.onSwipeUp();
                }
            }
        }
    }

    onSwipeLeft = () => {};
    onSwipeRight = () => {};
    onSwipeUp = () => {};
    onSwipeDown = () => {};
}

class QuizCacheManager {
    constructor() {
        this.storageKey = 'quiz-cache';
        this.cache = JSON.parse(localStorage.getItem(this.storageKey) || '{}');
    }

    save(key, data) {
        this.cache[key] = {
            data,
            timestamp: Date.now()
        };
        this.persistCache();
    }

    get(key) {
        return this.cache[key]?.data;
    }

    clear() {
        this.cache = {};
        this.persistCache();
    }

    persistCache() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.cache));
    }
}

// Animações personalizadas
const animations = {
    fadeIn: [
        { opacity: 0 },
        { opacity: 1 }
    ],
    slideIn: [
        { transform: 'translateY(20px)', opacity: 0 },
        { transform: 'translateY(0)', opacity: 1 }
    ],
    shake: [
        { transform: 'translateX(0)' },
        { transform: 'translateX(-10px)' },
        { transform: 'translateX(10px)' },
        { transform: 'translateX(0)' }
    ]
};

// Atalhos de teclado globais
const keyboardShortcuts = {
    'Alt+1': () => document.querySelector('#tipo1')?.click(),
    'Alt+2': () => document.querySelector('#tipo2')?.click(),
    'Alt+3': () => document.querySelector('#tipo3')?.click(),
    'Alt+R': () => document.querySelector('.btn-revisao')?.click(),
    'Alt+N': () => document.querySelector('.btn-anotacao')?.click(),
    'Alt+S': () => document.querySelector('.btn-sound')?.click(),
    'Alt+T': () => document.querySelector('.btn-theme')?.click(),
    'Alt+H': () => document.querySelector('.btn-help')?.click(),
    'Alt+P': () => document.querySelector('.btn-pause')?.click(),
    'Escape': () => document.querySelector('.btn-close')?.click()
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    const themeManager = new QuizThemeManager();
    const soundManager = new QuizSoundManager();
    const cacheManager = new QuizCacheManager();
    
    // Atalhos de teclado
    document.addEventListener('keydown', (e) => {
        const shortcut = `${e.altKey ? 'Alt+' : ''}${e.key}`;
        if (keyboardShortcuts[shortcut]) {
            e.preventDefault();
            keyboardShortcuts[shortcut]();
        }
    });

    // Gestos touch
    const gestureManager = new QuizGestureManager(document.body);
    gestureManager.onSwipeLeft = () => document.querySelector('.btn-next')?.click();
    gestureManager.onSwipeRight = () => document.querySelector('.btn-prev')?.click();
    gestureManager.onSwipeUp = () => document.querySelector('.btn-revisao')?.click();
    gestureManager.onSwipeDown = () => document.querySelector('.btn-anotacao')?.click();
});
