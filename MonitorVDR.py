<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carrusel Vertical de Recepciones (VDR)</title>
    <style>
        :root {
            --color-green: #2E7D32;
            --color-orange: #F57C00;
            --color-red: #D32F2F;
            --color-gray: #757575;
            --color-blue: #1976D2;
            --card-bg: #FFFFFF;
            --card-border-radius: 12px;
            --shadow: 0 4px 12px rgba(0,0,0,0.1);
            --shadow-active: 0 0 20px rgba(46,125,50,0.4);
            --transition-speed: 0.4s;
            --card-width: 90%;
            --card-max-width: 600px;
            --gap: 16px;
            --font-stack: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            --mono-font: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: var(--font-stack);
            background: #f0f4f8;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .carousel-wrapper {
            position: relative;
            width: 100%;
            max-width: var(--card-max-width);
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .carousel-viewport {
            width: 100%;
            height: 440px; /* Ajustable según contenido */
            overflow: hidden;
            position: relative;
            border-radius: var(--card-border-radius);
        }
        .carousel-track {
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform var(--transition-speed) ease-in-out;
        }
        .vdr-card {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: var(--card-width);
            max-width: 100%;
            background: var(--card-bg);
            border-radius: var(--card-border-radius);
            box-shadow: var(--shadow);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            transition: box-shadow var(--transition-speed), transform 0.3s ease;
            /* El posicionamiento vertical se define dinámicamente en JS */
            opacity: 0.7;
            filter: brightness(0.95);
        }
        .vdr-card.active {
            opacity: 1;
            filter: brightness(1);
            box-shadow: var(--shadow-active);
            border: 2px solid var(--color-green);
            z-index: 3;
            /* Pequeño aumento de tamaño */
            transform: translateX(-50%) scale(1.02);
        }
        .product-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1a1a1a;
            line-height: 1.3;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: default;
        }
        .product-title[title] {
            cursor: help;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            width: fit-content;
            color: white;
        }
        .status-badge.integrada { background-color: var(--color-green); }
        .status-badge.en-validacion { background-color: var(--color-orange); }
        .status-badge.pendiente-por-validar { background-color: var(--color-red); }
        .status-badge.anulada { background-color: var(--color-gray); }
        .status-badge.other { background-color: var(--color-gray); }
        .progress-container {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .progress-bar-wrapper {
            flex: 1;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: var(--color-green);
            transition: width 0.5s ease;
            border-radius: 4px;
        }
        .progress-fill.over {
            background: var(--color-blue);
        }
        .progress-text {
            font-family: var(--mono-font);
            font-size: 0.9rem;
            color: #333;
            white-space: nowrap;
        }
        .info-row {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            color: #424242;
        }
        .info-row span {
            font-family: var(--mono-font);
            font-size: 0.85rem;
        }
        .icon {
            font-size: 1rem;
            vertical-align: middle;
        }
        /* Controles de navegación */
        .nav-controls {
            display: flex;
            gap: 12px;
            margin: 16px 0;
        }
        .nav-btn {
            background: #e0e0e0;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 1.2rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        .nav-btn:hover {
            background: var(--color-green);
            color: white;
        }
        /* Dots */
        .dots {
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }
        .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #bbb;
            cursor: pointer;
            transition: background 0.2s;
        }
        .dot.active-dot {
            background: var(--color-green);
            transform: scale(1.2);
        }
        /* Mensaje de estado vacío */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-size: 1.1rem;
        }
        /* Responsive */
        @media (max-width: 480px) {
            .carousel-viewport {
                height: 400px;
            }
            .vdr-card {
                padding: 16px;
            }
            .product-title {
                font-size: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="carousel-wrapper" role="region" aria-label="Carrusel vertical de recepciones" aria-roledescription="carousel">
        <button class="nav-btn prev" aria-label="Recepción anterior" title="Anterior">▲</button>
        <div class="carousel-viewport" id="viewport">
            <div class="carousel-track" id="track">
                <!-- Las tarjetas se insertan dinámicamente -->
            </div>
        </div>
        <button class="nav-btn next" aria-label="Recepción siguiente" title="Siguiente">▼</button>
        <div class="dots" id="dots"></div>
        <div aria-live="polite" class="sr-only" id="announce"></div>
    </div>

    <script>
        (function() {
            // ====================================================================
            // DATOS DE EJEMPLO (extraídos del archivo Excel proporcionado)
            // Cada objeto representa una fila (VDR + producto)
            // ====================================================================
            const sampleData = [
                { Q: "DETERGENTE EN POLVO FRAGANCIA CITRICA LAS LLAVES 900 GR", AB: 50, AD: 50, G: "Integrada", H: "ODC-01-001-00015743", Y: "ALIMENTOS POLAR COMERCIAL, C.A." },
                { Q: "CERVEZA POLAR LIGHT RET 222ML", AB: 540, AD: 540, G: "Integrada", H: "ODC-01-001-00015805", Y: "CERVECERIA POLAR, C.A." },
                { Q: "REFRESCO ZERO PEPSI 2L", AB: 12, AD: 12, G: "Integrada", H: "ODC-01-001-00015798", Y: "PEPSI-COLA VENEZUELA C.A." },
                { Q: "BEBIDA ACHOCOLATADA CHOCOLISTO 200 GR", AB: 24, AD: 24, G: "Integrada", H: "ODC-01-001-00015487", Y: "PROCESADORA NATURALYST, S.A." },
                { Q: "LECHE ENTERA UHT NATULAC 946 ML", AB: 120, AD: 120, G: "Integrada", H: "ODC-01-001-00015510", Y: "INDUSTRIAS MAROS, C.A." },
                { Q: "NÉCTAR DE DURAZNO NATULAC TP 250ML", AB: 72, AD: 72, G: "Integrada", H: "ODC-01-001-00015699", Y: "INDUSTRIAS MAROS, C.A." },
                { Q: "SALCHICHA WIENER HERMO 225 gr", AB: 20, AD: 20, G: "Integrada", H: "ODC-01-001-00013740", Y: "INDUSTRIAS ALIMENTICIAS HERMO DE VENEZUELA S.A. (HERMO S.A.)" },
                { Q: "MORTADELA DE POLLO SUPERIOR HERMO 1 KG.", AB: 20, AD: 15, G: "En validación", H: "ODC-01-001-00013740", Y: "INDUSTRIAS ALIMENTICIAS HERMO DE VENEZUELA S.A. (HERMO S.A.)" },
                { Q: "PAÑAL ACTIVESEC DISNEY TALLA XG HUGGIES 25 UND", AB: 24, AD: 8, G: "Pendiente por validar", H: "ODC-01-005-00013785", Y: "DIMASSI, C.A." },
                { Q: "JAMON ESPALDA AHUMADA VISKING DELGADO ALIMEX 1.6 KG", AB: 21, AD: 0, G: "Anulada", H: "ODC-01-016-00016341", Y: "PRODUCTOS ALIMEX, C.A." }
            ];

            // Mapeo a los nombres de campo esperados internamente
            const data = sampleData.map(item => ({
                producto: item.Q,
                esperado: Number(item.AB) || 0,
                recibido: Number(item.AD) || 0,
                estatus: item.G,
                odc: item.H,
                proveedor: item.Y
            }));

            // ====================================================================
            // ELEMENTOS DEL DOM
            // ====================================================================
            const track = document.getElementById('track');
            const viewport = document.getElementById('viewport');
            const dotsContainer = document.getElementById('dots');
            const announcer = document.getElementById('announce');
            const prevBtn = document.querySelector('.prev');
            const nextBtn = document.querySelector('.next');

            // ====================================================================
            // ESTADO
            // ====================================================================
            let currentIndex = 0;
            let items = [...data]; // Podría clonarse para loop infinito
            let totalItems = items.length;
            let autoPlayTimer = null;
            let isPaused = false;

            // ====================================================================
            // FUNCIONES AUXILIARES
            // ====================================================================
            function getStatusClass(estatus) {
                const normalized = estatus.trim().toLowerCase().replace(/\s+/g, '-');
                if (normalized === 'integrada') return 'integrada';
                if (normalized.includes('en-validacion') || normalized === 'en validación') return 'en-validacion';
                if (normalized.includes('pendiente-por-validar') || normalized === 'pendiente por validar') return 'pendiente-por-validar';
                if (normalized === 'anulada') return 'anulada';
                return 'other';
            }

            function createCardHTML(item, isActive = false) {
                const progressPercent = Math.min(100, Math.round((item.recibido / (item.esperado || 1)) * 100));
                const over = item.recibido > item.esperado;
                const progressClass = over ? 'over' : '';
                const statusClass = getStatusClass(item.estatus);
                const progressText = `${item.recibido} / ${item.esperado}`;
                const truncatedProducto = item.producto.length > 40 ? item.producto.substring(0,40) + '...' : item.producto;

                return `
                    <div class="vdr-card${isActive ? ' active' : ''}" role="group" aria-roledescription="recepcion" aria-label="${item.producto}">
                        <div class="product-title" title="${item.producto}">${truncatedProducto}</div>
                        <span class="status-badge ${statusClass}">${item.estatus}</span>
                        <div class="progress-container">
                            <div class="progress-bar-wrapper">
                                <div class="progress-fill ${progressClass}" style="width: ${progressPercent}%;"></div>
                            </div>
                            <div class="progress-text">${progressText} (${progressPercent}%)</div>
                        </div>
                        <div class="info-row">
                            <span class="icon">📄</span> ODC: <span>${item.odc}</span>
                        </div>
                        <div class="info-row">
                            <span class="icon">🏭</span> Proveedor: <span>${item.proveedor}</span>
                        </div>
                    </div>
                `;
            }

            function renderDots(activeIdx) {
                dotsContainer.innerHTML = '';
                for (let i = 0; i < totalItems; i++) {
                    const dot = document.createElement('div');
                    dot.className = 'dot' + (i === activeIdx ? ' active-dot' : '');
                    dot.addEventListener('click', () => goToSlide(i));
                    dot.setAttribute('aria-label', `Ir a recepción ${i+1}`);
                    dotsContainer.appendChild(dot);
                }
            }

            function buildCarousel() {
                // Si no hay datos, vacío
                if (totalItems === 0) {
                    track.innerHTML = '';
                    dotsContainer.innerHTML = '';
                    return;
                }

                // Para 1 solo elemento, no hay loop
                if (totalItems === 1) {
                    track.innerHTML = createCardHTML(items[0], true);
                    // Desactivamos controles
                    prevBtn.style.visibility = 'hidden';
                    nextBtn.style.visibility = 'hidden';
                    dotsContainer.innerHTML = '';
                    return;
                }

                // Para varios elementos, implementamos clonación para loop infinito
                // La lógica: en el track tendremos [clon del último, ...items originales..., clon del primero]
                const lastClone = {...items[totalItems-1], _clone: true};
                const firstClone = {...items[0], _clone: true};
                const allItems = [lastClone, ...items, firstClone];

                // Limpiar track
                track.innerHTML = '';
                allItems.forEach((item, idx) => {
                    const isActive = idx === 1 ? true : false; // el primero después del clon es el índice 0 real
                    const card = document.createElement('div');
                    card.className = `vdr-card${isActive ? ' active' : ''}`;
                    // Cálculo de posición vertical
                    // Cada tarjeta ocupa aprox 350px de altura (ajustamos según contenido)
                    const cardHeight = 350; // altura fija aproximada
                    const posY = (idx - 1) * cardHeight; 
                    card.style.top = `${posY}px`;
                    card.innerHTML = `
                        <div class="product-title" title="${item.producto}">${item.producto.length > 40 ? item.producto.substring(0,40)+'...' : item.producto}</div>
                        <span class="status-badge ${getStatusClass(item.estatus)}">${item.estatus}</span>
                        <div class="progress-container">
                            <div class="progress-bar-wrapper">
                                <div class="progress-fill${item.recibido > item.esperado ? ' over' : ''}" style="width: ${Math.min(100, Math.round((item.recibido/(item.esperado||1))*100))}%;"></div>
                            </div>
                            <div class="progress-text">${item.recibido} / ${item.esperado} (${Math.round((item.recibido/(item.esperado||1))*100)}%)</div>
                        </div>
                        <div class="info-row"><span class="icon">📄</span> ODC: <span>${item.odc}</span></div>
                        <div class="info-row"><span class="icon">🏭</span> Proveedor: <span>${item.proveedor}</span></div>
                    `;
                    track.appendChild(card);
                });

                // Inicializar posición
                currentIndex = 0;
                track.style.transform = 'translateY(0px)';
                updateActiveCard();
                renderDots(currentIndex);
            }

            function updateActiveCard() {
                const cards = track.querySelectorAll('.vdr-card');
                cards.forEach(card => card.classList.remove('active'));
                // La tarjeta activa es la segunda en la lista (índice 1 = elemento real actual)
                if (cards.length >= 2) {
                    cards[1].classList.add('active');
                }
            }

            function goToSlide(index) {
                if (totalItems <= 1) return;
                currentIndex = index;
                const offset = - (index + 1) * 350; // +1 por el clon al inicio
                track.style.transition = 'transform 0.4s ease-in-out';
                track.style.transform = `translateY(${offset}px)`;
                updateDots(index);
                announcer.textContent = `Recepción ${index+1} de ${totalItems}, ${items[index].producto}`;
            }

            function handleTransitionEnd() {
                // Verificar si hemos llegado al clon (extremos)
                const totalElements = totalItems + 2; // originales + dos clones
                // Si estamos en el clon del primer elemento (después de avanzar hacia abajo desde el último)
                if (currentIndex === totalItems) { // más allá del último, saltamos al primero real
                    // Movemos instantáneamente al índice 0 real (posición 1 del array)
                    track.style.transition = 'none';
                    const offset = - (0 + 1) * 350;
                    track.style.transform = `translateY(${offset}px)`;
                    currentIndex = 0;
                    updateDots(currentIndex);
                    updateActiveCard();
                    // Forzamos reflow
                    track.offsetHeight;
                    track.style.transition = 'transform 0.4s ease-in-out';
                } else if (currentIndex === -1) { // antes del primer elemento, saltamos al último real
                    track.style.transition = 'none';
                    const offset = - (totalItems-1 + 1) * 350;
                    track.style.transform = `translateY(${offset}px)`;
                    currentIndex = totalItems - 1;
                    updateDots(currentIndex);
                    updateActiveCard();
                    track.offsetHeight;
                    track.style.transition = 'transform 0.4s ease-in-out';
                }
            }

            function updateDots(index) {
                const dots = document.querySelectorAll('.dot');
                dots.forEach((dot, i) => {
                    dot.classList.toggle('active-dot', i === index);
                });
            }

            function next() {
                if (totalItems <= 1) return;
                currentIndex++;
                if (currentIndex >= totalItems) {
                    // Reiniciar al 0 real, pero usando el clon ya desplazado
                    currentIndex = totalItems; // marca para salto en transitionend
                }
                const offset = - (currentIndex + 1) * 350;
                track.style.transform = `translateY(${offset}px)`;
            }

            function prev() {
                if (totalItems <= 1) return;
                currentIndex--;
                if (currentIndex < 0) {
                    currentIndex = -1; // marca para salto
                }
                const offset = - (currentIndex + 1) * 350;
                track.style.transform = `translateY(${offset}px)`;
            }

            function startAutoPlay() {
                stopAutoPlay();
                if (totalItems > 1) {
                    autoPlayTimer = setInterval(next, 8000);
                }
            }

            function stopAutoPlay() {
                if (autoPlayTimer) clearInterval(autoPlayTimer);
            }

            // ====================================================================
            // EVENTOS
            // ====================================================================
            prevBtn.addEventListener('click', () => {
                prev();
                stopAutoPlay();
                startAutoPlay();
            });
            nextBtn.addEventListener('click', () => {
                next();
                stopAutoPlay();
                startAutoPlay();
            });

            viewport.addEventListener('mouseenter', () => stopAutoPlay());
            viewport.addEventListener('mouseleave', () => {
                if (!isPaused) startAutoPlay();
            });

            // Swipe vertical básico
            let touchStartY = 0;
            viewport.addEventListener('touchstart', (e) => {
                touchStartY = e.touches[0].clientY;
                stopAutoPlay();
            });
            viewport.addEventListener('touchend', (e) => {
                if (!touchStartY) return;
                const touchEndY = e.changedTouches[0].clientY;
                const diff = touchStartY - touchEndY;
                if (Math.abs(diff) > 40) {
                    if (diff > 0) {
                        // swipe up -> siguiente
                        next();
                    } else {
                        // swipe down -> anterior
                        prev();
                    }
                }
                startAutoPlay();
                touchStartY = 0;
            });

            // Teclado
            window.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    next();
                    stopAutoPlay();
                    startAutoPlay();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    prev();
                    stopAutoPlay();
                    startAutoPlay();
                }
            });

            track.addEventListener('transitionend', handleTransitionEnd);

            // ====================================================================
            // INICIALIZAR
            // ====================================================================
            if (data.length === 0) {
                viewport.innerHTML = '<div class="empty-state">No hay recepciones disponibles.</div>';
                prevBtn.style.display = 'none';
                nextBtn.style.display = 'none';
            } else {
                buildCarousel();
                startAutoPlay();
            }

            // Limpiar interval al cerrar
            window.addEventListener('beforeunload', () => stopAutoPlay());
        })();
    </script>
</body>
</html>
