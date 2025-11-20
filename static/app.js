// Estado da aplicação
let validationData = null;

// Elementos DOM
const addSourceForm = document.getElementById('addSourceForm');
const sourceUrlInput = document.getElementById('sourceUrl');
const sourceNameInput = document.getElementById('sourceName');
const validateBtn = document.getElementById('validateBtn');
const addBtn = document.getElementById('addBtn');
const validationResult = document.getElementById('validationResult');
const validationContent = document.getElementById('validationContent');
const sourcesContainer = document.getElementById('sourcesContainer');
const loadingSpinner = document.getElementById('loadingSpinner');
const refreshBtn = document.getElementById('refreshBtn');

// Event Listeners
validateBtn.addEventListener('click', validateSource);
addBtn.addEventListener('click', addSource);
refreshBtn.addEventListener('click', loadSources);

// Carrega fontes ao iniciar
loadSources();

// Funções
async function validateSource() {
    const url = sourceUrlInput.value.trim();
    const name = sourceNameInput.value.trim();

    if (!url) {
        alert('Por favor, insira uma URL');
        return;
    }

    // UI feedback
    validateBtn.disabled = true;
    validateBtn.textContent = '⏳ Validando...';
    validationResult.style.display = 'none';

    try {
        const response = await fetch('/api/sources/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, name })
        });

        const data = await response.json();

        if (data.success) {
            validationData = data.data;
            displayValidationResult(data.data);
            addBtn.disabled = false;
        } else {
            displayValidationError(data.error);
            addBtn.disabled = true;
        }
    } catch (error) {
        displayValidationError(error.message);
        addBtn.disabled = true;
    } finally {
        validateBtn.disabled = false;
        validateBtn.textContent = '🔍 Validar Fonte';
    }
}

function displayValidationResult(data) {
    validationResult.style.display = 'block';
    
    const score = data.validation_score;
    let scoreClass = 'score-low';
    let resultClass = 'validation-error';
    
    if (score >= 8) {
        scoreClass = 'score-high';
        resultClass = 'validation-success';
    } else if (score >= 5) {
        scoreClass = 'score-medium';
        resultClass = 'validation-warning';
    }
    
    validationResult.className = `validation-result ${resultClass}`;
    
    let html = `
        <div style="margin-bottom: 1rem;">
            <strong>Score de Validação:</strong> 
            <span class="score-badge ${scoreClass}">${score}/10</span>
        </div>
    `;
    
    if (data.rss_found && data.rss_found.length > 0) {
        html += `
            <div style="margin-bottom: 1rem;">
                <strong>✅ RSS Feed Encontrado!</strong><br>
                <small>URL: ${data.recommended_url}</small><br>
                <small>Nome: ${data.recommended_name || 'Detectado automaticamente'}</small>
            </div>
        `;
    } else if (data.can_scrape_html) {
        html += `
            <div style="margin-bottom: 1rem;">
                <strong>⚠️ RSS não encontrado, mas HTML scraping funciona</strong><br>
                <small>O sistema consegue extrair notícias do HTML da página</small>
            </div>
        `;
    } else {
        html += `
            <div style="margin-bottom: 1rem;">
                <strong>❌ Não foi possível extrair notícias</strong><br>
                <small>Tente outra URL ou verifique se o site tem RSS feed</small>
            </div>
        `;
    }
    
    if (data.sample_news && data.sample_news.length > 0) {
        html += `
            <div class="sample-news">
                <strong>📰 Notícias Encontradas (${data.sample_news.length} exemplos):</strong>
                ${data.sample_news.map(news => `
                    <div class="news-item">
                        <h4>${news.title}</h4>
                        <p>${news.summary}</p>
                        <small>${news.pubDate ? new Date(news.pubDate).toLocaleDateString('pt-BR') : 'Data não disponível'}</small>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    validationContent.innerHTML = html;
}

function displayValidationError(error) {
    validationResult.style.display = 'block';
    validationResult.className = 'validation-result validation-error';
    validationContent.innerHTML = `
        <strong>❌ Erro na Validação</strong><br>
        <p>${error}</p>
    `;
}

async function addSource() {
    if (!validationData || validationData.validation_score === 0) {
        alert('Por favor, valide a fonte primeiro');
        return;
    }

    addBtn.disabled = true;
    addBtn.textContent = '⏳ Adicionando...';

    try {
        const response = await fetch('/api/sources/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: sourceUrlInput.value.trim(),
                name: sourceNameInput.value.trim()
            })
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ Fonte adicionada com sucesso!');
            
            // Limpa formulário
            sourceUrlInput.value = '';
            sourceNameInput.value = '';
            validationResult.style.display = 'none';
            validationData = null;
            addBtn.disabled = true;
            
            // Recarrega lista
            loadSources();
        } else {
            alert(`❌ Erro: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Erro: ${error.message}`);
    } finally {
        addBtn.textContent = '✅ Adicionar ao Banco';
    }
}

async function loadSources() {
    loadingSpinner.style.display = 'block';
    sourcesContainer.innerHTML = '';

    try {
        const response = await fetch('/api/sources');
        const data = await response.json();

        if (data.success) {
            displaySources(data.sources);
        } else {
            sourcesContainer.innerHTML = `
                <div class="empty-state">
                    <h3>❌ Erro ao carregar fontes</h3>
                </div>
            `;
        }
    } catch (error) {
        sourcesContainer.innerHTML = `
            <div class="empty-state">
                <h3>❌ Erro ao carregar fontes</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

function displaySources(sources) {
    if (sources.length === 0) {
        sourcesContainer.innerHTML = `
            <div class="empty-state">
                <h3>📭 Nenhuma fonte cadastrada</h3>
                <p>Adicione sua primeira fonte usando o formulário acima</p>
            </div>
        `;
        return;
    }

    const html = `
        <div class="sources-grid">
            ${sources.map(source => `
                <div class="source-card ${source.active ? '' : 'inactive'}">
                    <div class="source-header">
                        <div class="source-info">
                            <h3>${source.name || 'Sem nome'}</h3>
                            <a href="${source.url}" target="_blank" class="source-url">${source.url}</a>
                        </div>
                    </div>
                    
                    <div class="source-badges">
                        <span class="badge badge-${source.type}">${source.type.toUpperCase()}</span>
                        <span class="badge badge-${source.active ? 'active' : 'inactive'}">
                            ${source.active ? '✅ Ativa' : '❌ Inativa'}
                        </span>
                        ${source.validation_score ? `
                            <span class="badge score-${source.validation_score >= 8 ? 'high' : source.validation_score >= 5 ? 'medium' : 'low'}">
                                Score: ${source.validation_score}/10
                            </span>
                        ` : ''}
                    </div>
                    
                    <div class="source-meta">
                        <span>📅 Criado: ${new Date(source.created_at).toLocaleDateString('pt-BR')}</span>
                        ${source.validated_at ? `
                            <span>✅ Validado: ${new Date(source.validated_at).toLocaleDateString('pt-BR')}</span>
                        ` : ''}
                    </div>
                    
                    <div class="source-actions">
                        <button 
                            class="btn btn-small ${source.active ? 'btn-secondary' : 'btn-success'}" 
                            onclick="toggleSource(${source.id})"
                        >
                            ${source.active ? '⏸️ Desativar' : '▶️ Ativar'}
                        </button>
                        <button 
                            class="btn btn-small btn-danger" 
                            onclick="deleteSource(${source.id}, '${source.name}')"
                        >
                            🗑️ Deletar
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    sourcesContainer.innerHTML = html;
}

async function toggleSource(id) {
    try {
        const response = await fetch(`/api/sources/${id}/toggle`, {
            method: 'PATCH'
        });

        const data = await response.json();

        if (data.success) {
            loadSources();
        } else {
            alert('❌ Erro ao alterar status da fonte');
        }
    } catch (error) {
        alert(`❌ Erro: ${error.message}`);
    }
}

async function deleteSource(id, name) {
    if (!confirm(`Tem certeza que deseja deletar "${name}"?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/sources/${id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ Fonte deletada com sucesso!');
            loadSources();
        } else {
            alert('❌ Erro ao deletar fonte');
        }
    } catch (error) {
        alert(`❌ Erro: ${error.message}`);
    }
}
