class SimuladoManager {
    constructor() {
        this.tempoRestante = 0;
        this.tempoQuestao = 0;
        this.intervalTimer = null;
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.swipeThreshold = 100;
    }

    init(tempoTotal) {
        this.tempoRestante = tempoTotal;
        this.initTimer();
        this.initEventListeners();
        this.initKeyboardShortcuts();
        this.initTouchEvents();
    }

    initTimer() {
        const timerElement = document.getElementById('timer');
        
        this.intervalTimer = setInterval(() => {
            if (this.tempoRestante <= 0) {
                this.finalizarPorTempo();
                return;
            }

            if (this.tempoRestante <= 300) {
                timerElement.classList.add('timer-warning');
                if (this.tempoRestante === 300) {
                    this.alertarTempoRestante();
                }
            }

            timerElement.textContent = this.formatarTempo(this.tempoRestante);
            this.tempoRestante--;
            this.tempoQuestao++;
        }, 1000);
    }

    initEventListeners() {
        document.querySelectorAll('.alternativa').forEach(alt => {
            alt.addEventListener('click', (e) => {
                if (e.target.tagName !== 'INPUT') {
                    const input = alt.querySelector('input');
                    if (input) input.click();
                }
                this.selecionarAlternativa(alt);
            });
        });

        // Salvar progresso automaticamente
        setInterval(() => this.salvarProgresso(), 30000);
    }

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (document.activeElement.tagName === 'TEXTAREA') return;

            const shortcuts = {
                '1': () => this.selecionarAlternativaPorNumero(1),
                '2': () => this.selecionarAlternativaPorNumero(2),
                '3': () => this.selecionarAlternativaPorNumero(3),
                '4': () => this.selecionarAlternativaPorNumero(4),
                '5': () => this.selecionarAlternativaPorNumero(5),
                'ArrowLeft': () => this.navegarQuestao('anterior'),
                'ArrowRight': () => this.navegarQuestao('proxima'),
                'r': () => this.marcarRevisao(),
                'n': () => this.abrirAnotacoes(),
            };

            if (shortcuts[e.key]) {
                e.preventDefault();
                shortcuts[e.key]();
            }
        });
    }

    initTouchEvents() {
        document.addEventListener('touchstart', e => {
            this.touchStartX = e.changedTouches[0].screenX;
        });

        document.addEventListener('touchend', e => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        });
    }

    handleSwipe() {
        const diff = this.touchEndX - this.touchStartX;
        if (Math.abs(diff) < this.swipeThreshold) return;

        if (diff > 0) {
            this.navegarQuestao('anterior');
        } else {
            this.navegarQuestao('proxima');
        }
    }

    selecionarAlternativa(elemento) {
        document.querySelectorAll('.alternativa').forEach(alt => {
            alt.classList.remove('selected');
        });
        elemento.classList.add('selected');
        elemento.classList.add('animate-fade');
    }

    selecionarAlternativaPorNumero(numero) {
        const alternativa = document.querySelector(`#alt${numero}`);
        if (alternativa) {
            alternativa.click();
        }
    }

    navegarQuestao(direcao) {
        const btn = direcao === 'anterior' ? 
            document.querySelector('.btn-secondary') : 
            document.querySelector('.btn-primary');
        if (btn) btn.click();
    }

    salvarProgresso() {
        const data = {
            tempoRestante: this.tempoRestante,
            respostaSelecionada: document.querySelector('input[name="resposta"]:checked')?.value,
            tempoQuestao: this.tempoQuestao
        };
        localStorage.setItem('simuladoProgresso', JSON.stringify(data));
    }

    formatarTempo(segundos) {
        const horas = Math.floor(segundos / 3600);
        const minutos = Math.floor((segundos % 3600) / 60);
        const segs = segundos % 60;
        return `${String(horas).padStart(2, '0')}:${String(minutos).padStart(2, '0')}:${String(segs).padStart(2, '0')}`;
    }

    finalizarPorTempo() {
        clearInterval(this.intervalTimer);
        Swal.fire({
            title: 'Tempo Esgotado!',
            text: 'O tempo para realização do simulado acabou.',
            icon: 'warning',
            showConfirmButton: false,
            timer: 3000
        }).then(() => {
            window.location.href = '/simulados/resultado/1';
        });
    }

    alertarTempoRestante() {
        Swal.fire({
            title: 'Atenção!',
            text: 'Faltam apenas 5 minutos!',
            icon: 'warning',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 5000
        });
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    const simulado = new SimuladoManager();
    simulado.init(window.tempoRestante || 7200);
});
