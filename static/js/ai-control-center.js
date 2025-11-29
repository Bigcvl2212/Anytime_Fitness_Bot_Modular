(function (window) {
    'use strict';

    const state = {
        root: null,
        knowledgeBase: { categories: {}, documents: {} },
        currentCategory: 'all',
        modals: {},
        bootstrap: window.bootstrap || null,
        memberSearchTimeout: null,
        selectedMember: null
    };

    const getBootstrap = () => state.bootstrap || window.bootstrap || null;

    const els = {};

    const ready = (cb) => {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', cb, { once: true });
        } else {
            cb();
        }
    };

    const getModal = (id) => {
        const modalLib = getBootstrap();
        if (!modalLib) return null;
        if (!state.modals[id]) {
            const node = document.getElementById(id);
            if (!node) return null;
            state.modals[id] = modalLib.Modal.getOrCreateInstance(node);
        }
        return state.modals[id];
    };

    const closeModal = (id) => {
        const modal = state.modals[id];
        if (modal) modal.hide();
    };

    const showStatusMessage = (target, message, isError = false) => {
        if (!target) return;
        target.innerHTML = `
            <div class="ai-empty-state ${isError ? 'text-danger' : ''}">
                ${message}
            </div>
        `;
    };

    const cacheElements = () => {
        els.workerDot = document.getElementById('aiWorkerDot');
        els.workerStatus = document.getElementById('aiWorkerStatusText');
        els.workflowGrid = document.getElementById('aiWorkflowGrid');
        els.workflowRefreshBtn = document.querySelector('[data-ai-action="refresh-workflows"]');
        els.knowledgeCategories = document.getElementById('aiKnowledgeCategories');
        els.knowledgeDocuments = document.getElementById('aiKnowledgeDocuments');
        els.docCategorySelect = document.getElementById('aiDocCategory');
        els.addDocumentForm = document.getElementById('aiAddDocumentForm');
        els.viewDocTitle = document.getElementById('aiDocViewTitle');
        els.viewDocMeta = document.getElementById('aiDocViewMeta');
        els.viewDocContent = document.getElementById('aiDocViewContent');
        els.paymentPlansList = document.getElementById('aiPaymentPlansList');
        els.addPaymentPlanForm = document.getElementById('aiAddPaymentPlanForm');
        els.memberNameInput = document.getElementById('aiPaymentPlanMemberName');
        els.memberSearchResults = document.getElementById('aiMemberSearchResults');
        els.recordPaymentForm = document.getElementById('aiRecordPaymentForm');
        els.copyDocBtn = document.getElementById('aiCopyDocBtn');
        els.categoryBadge = document.getElementById('aiSelectedCategory');
    };

    const bindEvents = () => {
        const actionMap = {
            'refresh-workflows': () => { loadWorkflows(); loadPaymentPlans(); },
            'start-worker': startWorker,
            'stop-worker': stopWorker,
            'show-add-document': () => openModal('aiAddDocumentModal'),
            'show-add-payment-plan': () => {
                state.selectedMember = null;
                if (els.memberNameInput) els.memberNameInput.value = '';
                if (els.memberSearchResults) els.memberSearchResults.innerHTML = '';
                const startDateInput = document.getElementById('aiPaymentPlanStartDate');
                if (startDateInput) startDateInput.valueAsDate = new Date();
                openModal('aiAddPaymentPlanModal');
            }
        };

        state.root?.addEventListener('click', (evt) => {
            const action = evt.target?.closest('[data-ai-action]')?.dataset?.aiAction;
            if (action && actionMap[action]) {
                evt.preventDefault();
                actionMap[action]();
            }
        });

        els.addDocumentForm?.addEventListener('submit', (evt) => {
            evt.preventDefault();
            addDocument();
        });

        els.addPaymentPlanForm?.addEventListener('submit', (evt) => {
            evt.preventDefault();
            addPaymentPlan();
        });

        els.recordPaymentForm?.addEventListener('submit', (evt) => {
            evt.preventDefault();
            recordPayment();
        });

        // Member name search with debounce
        els.memberNameInput?.addEventListener('input', (evt) => {
            clearTimeout(state.memberSearchTimeout);
            const query = evt.target.value.trim();
            if (query.length < 2) {
                if (els.memberSearchResults) els.memberSearchResults.innerHTML = '';
                return;
            }
            state.memberSearchTimeout = setTimeout(() => searchMembers(query), 300);
        });

        els.memberSearchResults?.addEventListener('click', (evt) => {
            const item = evt.target?.closest('[data-member-name]');
            if (item) {
                state.selectedMember = {
                    name: item.dataset.memberName,
                    id: item.dataset.memberId,
                    pastDue: parseFloat(item.dataset.pastDue || 0)
                };
                if (els.memberNameInput) els.memberNameInput.value = state.selectedMember.name;
                if (els.memberSearchResults) els.memberSearchResults.innerHTML = '';
                // Auto-fill past due amount
                const totalOwedInput = document.getElementById('aiPaymentPlanTotalOwed');
                if (totalOwedInput && state.selectedMember.pastDue > 0) {
                    totalOwedInput.value = state.selectedMember.pastDue.toFixed(2);
                }
            }
        });

        els.copyDocBtn?.addEventListener('click', copyDocumentContent);

        els.knowledgeCategories?.addEventListener('click', (evt) => {
            const btn = evt.target?.closest('[data-category]');
            if (!btn) return;
            evt.preventDefault();
            state.currentCategory = btn.dataset.category;
            renderCategories();
            renderDocuments();
        });

        els.knowledgeDocuments?.addEventListener('click', (evt) => {
            const viewBtn = evt.target?.closest('[data-doc-id][data-ai-view]');
            const deleteBtn = evt.target?.closest('[data-doc-id][data-ai-delete]');
            if (viewBtn) {
                const { docId, category } = viewBtn.dataset;
                viewDocument(docId, category);
            } else if (deleteBtn) {
                const { docId, category } = deleteBtn.dataset;
                deleteDocument(docId, category);
            }
        });

        els.workflowGrid?.addEventListener('change', (evt) => {
            const toggle = evt.target?.closest('[data-workflow][data-ai-toggle]');
            if (!toggle) return;
            const name = toggle.dataset.workflow;
            toggleWorkflow(name, toggle.checked);
        });

        els.workflowGrid?.addEventListener('click', (evt) => {
            const btn = evt.target?.closest('[data-workflow][data-ai-action]');
            if (!btn) return;
            const { aiAction, workflow } = btn.dataset;
            if (aiAction === 'run-workflow') {
                runWorkflow(workflow);
            } else if (aiAction === 'configure-workflow') {
                configureWorkflow(workflow);
            }
        });

        els.paymentPlansList?.addEventListener('click', (evt) => {
            const removeBtn = evt.target?.closest('[data-member-id][data-ai-remove-plan]');
            const recordBtn = evt.target?.closest('[data-member-id][data-ai-record-payment]');
            if (removeBtn) {
                removePlan(removeBtn.dataset.memberId);
            } else if (recordBtn) {
                openRecordPaymentModal(recordBtn.dataset);
            }
        });
    };

    const openModal = (id) => {
        const modal = getModal(id);
        if (modal) modal.show();
    };

    const init = () => {
        ready(() => {
            state.root = document.querySelector('[data-ai-control-panel]');
            if (!state.root) return;
            state.bootstrap = getBootstrap();
            cacheElements();
            bindEvents();
            hydrate();
        });
    };

    const hydrate = () => {
        loadWorkerStatus();
        loadWorkflows();
        loadKnowledgeBase();
        loadPaymentPlans();
    };

    // ========== Worker Status ==========
    const loadWorkerStatus = async () => {
        try {
            const resp = await fetch('/api/ai/worker/status');
            const data = await resp.json();
            const running = Boolean(data.running);
            els.workerDot?.classList.toggle('running', running);
            if (els.workerStatus) {
                els.workerStatus.textContent = running ? 'Worker online' : 'Worker offline';
            }
        } catch (error) {
            console.error('AI worker status error', error);
            if (els.workerStatus) {
                els.workerStatus.textContent = 'Unable to check worker status';
            }
        }
    };

    const startWorker = async () => {
        try {
            await fetch('/api/ai/worker/start', { method: 'POST' });
            await loadWorkerStatus();
        } catch (error) {
            console.error('Start worker error', error);
        }
    };

    const stopWorker = async () => {
        try {
            await fetch('/api/ai/worker/stop', { method: 'POST' });
            await loadWorkerStatus();
        } catch (error) {
            console.error('Stop worker error', error);
        }
    };

    // ========== Workflows ==========
    const loadWorkflows = async () => {
        if (els.workflowGrid) {
            els.workflowGrid.innerHTML = '<div class="py-4 text-center w-100 text-muted">Loading workflows...</div>';
        }
        try {
            const resp = await fetch('/api/ai/workflows');
            const data = await resp.json();
            if (data.success) {
                renderWorkflows(data.workflows || []);
            } else {
                showStatusMessage(els.workflowGrid, 'No workflows available');
            }
        } catch (error) {
            console.error('Workflow load error', error);
            showStatusMessage(els.workflowGrid, 'Failed to load workflows', true);
        }
    };

    const renderWorkflows = (workflows) => {
        if (!els.workflowGrid) return;
        if (!workflows.length) {
            showStatusMessage(els.workflowGrid, 'No workflows configured yet');
            return;
        }

        const rows = workflows.map((w) => `
            <div class="col-12 col-lg-6">
                <div class="ai-workflow-card ${w.enabled ? 'active' : ''}" data-workflow-card="${w.name}">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <div class="text-uppercase small text-muted">${w.category || 'general'}</div>
                            <h5 class="mt-1 mb-1">${w.display_name}</h5>
                            <p class="text-muted small mb-0">${w.description || ''}</p>
                        </div>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" role="switch"
                                   data-ai-toggle data-workflow="${w.name}" ${w.enabled ? 'checked' : ''}>
                        </div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="badge ${w.enabled ? 'bg-success' : 'bg-secondary'}">${w.enabled ? 'Enabled' : 'Disabled'}</span>
                            ${w.last_run ? `<span class="text-muted small ms-2">Last run ${formatDate(w.last_run)}</span>` : ''}
                        </div>
                        <div class="ai-workflow-actions d-flex gap-2">
                            <button class="btn btn-light btn-sm" data-workflow="${w.name}" data-ai-action="configure-workflow">
                                <i class="fas fa-sliders-h me-1"></i>Configure
                            </button>
                            <button class="btn btn-primary btn-sm" data-workflow="${w.name}" data-ai-action="run-workflow">
                                <i class="fas fa-play me-1"></i>Run
                            </button>
                        </div>
                    </div>
                </div>
            </div>`).join('');

        els.workflowGrid.innerHTML = rows;
    };

    const toggleWorkflow = async (name, enabled) => {
        try {
            const endpoint = enabled ? 'enable' : 'disable';
            const resp = await fetch(`/api/ai/workflows/${name}/${endpoint}`, { method: 'POST' });
            const data = await resp.json();
            if (!data.success) {
                await loadWorkflows();
                alert('Unable to update workflow state.');
            }
        } catch (error) {
            console.error('Toggle workflow error', error);
            await loadWorkflows();
        }
    };

    const runWorkflow = async (name) => {
        if (!confirm(`Run workflow "${name}" now?`)) return;
        try {
            const resp = await fetch(`/api/ai/workflows/${name}/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ force: true })
            });
            const data = await resp.json();
            if (!data.success) {
                alert(data.error || 'Workflow failed');
            } else {
                alert('Workflow completed successfully.');
            }
        } catch (error) {
            console.error('Run workflow error', error);
            alert('Unable to run workflow.');
        }
    };

    const configureWorkflow = async (name) => {
        const modal = getModal('aiWorkflowConfigModal');
        if (!modal) return;
        
        const title = document.getElementById('aiWorkflowConfigTitle');
        const body = document.getElementById('aiWorkflowConfigBody');
        
        if (title) title.textContent = `Configure Workflow`;
        if (body) body.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
        
        modal.show();
        
        try {
            const resp = await fetch('/api/ai/workflows');
            const data = await resp.json();
            
            if (!data.success) {
                body.innerHTML = '<div class="alert alert-danger">Failed to load workflow settings</div>';
                return;
            }
            
            const workflow = (data.workflows || []).find(w => w.name === name);
            if (!workflow) {
                body.innerHTML = '<div class="alert alert-warning">Workflow not found</div>';
                return;
            }
            
            if (title) title.textContent = `Configure: ${workflow.display_name}`;
            
            const config = workflow.config || {};
            body.innerHTML = buildConfigForm(name, workflow.display_name, config);
            
            const form = document.getElementById('aiWorkflowConfigForm');
            form?.addEventListener('submit', async (e) => {
                e.preventDefault();
                await saveWorkflowConfig(name, form);
            });
            
        } catch (error) {
            console.error('Config load error', error);
            body.innerHTML = '<div class="alert alert-danger">Error loading configuration</div>';
        }
    };
    
    const buildConfigForm = (workflowName, displayName, config) => {
        const configFields = {
            'auto_reply_messages': [
                { key: 'response_delay_seconds', label: 'Response Delay (seconds)', type: 'number', min: 0, max: 300, help: 'Wait time before AI responds' },
                { key: 'max_replies_per_hour', label: 'Max Replies Per Hour', type: 'number', min: 1, max: 100, help: 'Rate limit for auto-replies' },
                { key: 'require_approval', label: 'Require Human Approval', type: 'checkbox', help: 'Queue responses for review before sending' },
                { key: 'use_knowledge_base', label: 'Use Knowledge Base', type: 'checkbox', help: 'Include knowledge base context in responses' }
            ],
            'prospect_outreach': [
                { key: 'check_interval_minutes', label: 'Check Interval (minutes)', type: 'number', min: 1, max: 60, help: 'How often to check for new prospects' },
                { key: 'max_outreach_per_day', label: 'Max Outreach Per Day', type: 'number', min: 1, max: 200, help: 'Daily limit for prospect messages' },
                { key: 'schedule_follow_up_days', label: 'Follow-up After (days)', type: 'number', min: 1, max: 14, help: 'Days before sending follow-up' },
                { key: 'outreach_template', label: 'Outreach Template', type: 'select', options: ['default', 'casual', 'professional', 'promo'], help: 'Message style template' }
            ],
            'past_due_reminders': [
                { key: 'reminder_hour', label: 'Send Reminders At (hour)', type: 'number', min: 0, max: 23, help: '24-hour format (e.g., 9 = 9am)' },
                { key: 'max_reminders_per_day', label: 'Max Reminders Per Member Per Day', type: 'number', min: 1, max: 5, help: 'Limit reminder frequency' },
                { key: 'min_days_past_due', label: 'Min Days Past Due', type: 'number', min: 1, max: 90, help: 'Start reminders after this many days' },
                { key: 'urgency_threshold_days', label: 'Urgency Threshold (days)', type: 'number', min: 7, max: 90, help: 'Escalate urgency after this many days' },
                { key: 'respect_payment_plans', label: 'Respect Payment Plans', type: 'checkbox', help: 'Skip members with active payment plans' }
            ],
            'auto_lock_past_due': [
                { key: 'grace_period_days', label: 'Grace Period (days)', type: 'number', min: 1, max: 90, help: 'Days past due before locking access' },
                { key: 'warning_days_before', label: 'Warning Days Before Lock', type: 'number', min: 1, max: 14, help: 'Send warning this many days before lock' },
                { key: 'send_warning_before_lock', label: 'Send Warning Before Lock', type: 'checkbox', help: 'Notify member before locking' },
                { key: 'respect_payment_plans', label: 'Respect Payment Plans', type: 'checkbox', help: 'Don\'t lock members with active payment plans' },
                { key: 'require_confirmation', label: 'Require Manual Confirmation', type: 'checkbox', help: 'Queue lock actions for approval' }
            ],
            'square_invoice_automation': [
                { key: 'payment_due_days', label: 'Payment Due (days)', type: 'number', min: 1, max: 30, help: 'Days until invoice is due' },
                { key: 'late_fee_amount', label: 'Late Fee Amount ($)', type: 'number', min: 0, max: 100, step: '0.01', help: 'Late fee to add if applicable' },
                { key: 'auto_send', label: 'Auto-Send Invoices', type: 'checkbox', help: 'Send invoices automatically (vs draft)' },
                { key: 'include_late_fee', label: 'Include Late Fee', type: 'checkbox', help: 'Add late fee to past due invoices' }
            ]
        };
        
        const fields = configFields[workflowName] || [];
        
        if (fields.length === 0) {
            return `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    This workflow has no configurable options.
                </div>
            `;
        }
        
        const fieldHtml = fields.map(field => {
            const value = config[field.key] ?? '';
            const id = `config_${field.key}`;
            
            if (field.type === 'checkbox') {
                return `
                    <div class="mb-3">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="${id}" name="${field.key}" ${value ? 'checked' : ''}>
                            <label class="form-check-label" for="${id}">${field.label}</label>
                        </div>
                        ${field.help ? `<small class="text-muted d-block mt-1">${field.help}</small>` : ''}
                    </div>
                `;
            } else if (field.type === 'select') {
                const options = (field.options || []).map(opt => 
                    `<option value="${opt}" ${value === opt ? 'selected' : ''}>${opt.charAt(0).toUpperCase() + opt.slice(1)}</option>`
                ).join('');
                return `
                    <div class="mb-3">
                        <label class="form-label" for="${id}">${field.label}</label>
                        <select class="form-select" id="${id}" name="${field.key}">${options}</select>
                        ${field.help ? `<small class="text-muted d-block mt-1">${field.help}</small>` : ''}
                    </div>
                `;
            } else {
                const extraAttrs = [];
                if (field.min !== undefined) extraAttrs.push(`min="${field.min}"`);
                if (field.max !== undefined) extraAttrs.push(`max="${field.max}"`);
                if (field.step !== undefined) extraAttrs.push(`step="${field.step}"`);
                return `
                    <div class="mb-3">
                        <label class="form-label" for="${id}">${field.label}</label>
                        <input type="${field.type}" class="form-control" id="${id}" name="${field.key}" value="${value}" ${extraAttrs.join(' ')}>
                        ${field.help ? `<small class="text-muted d-block mt-1">${field.help}</small>` : ''}
                    </div>
                `;
            }
        }).join('');
        
        return `
            <form id="aiWorkflowConfigForm" data-workflow="${workflowName}">
                ${fieldHtml}
                <div class="d-flex justify-content-end gap-2 mt-4 pt-3 border-top">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save me-1"></i>Save Configuration
                    </button>
                </div>
            </form>
        `;
    };
    
    const saveWorkflowConfig = async (workflowName, form) => {
        const formData = new FormData(form);
        const config = {};
        
        for (const [key, value] of formData.entries()) {
            const input = form.querySelector(`[name="${key}"]`);
            if (input?.type === 'checkbox') {
                config[key] = input.checked;
            } else if (input?.type === 'number') {
                config[key] = parseFloat(value) || 0;
            } else {
                config[key] = value;
            }
        }
        
        form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            if (!formData.has(cb.name)) {
                config[cb.name] = false;
            }
        });
        
        try {
            const resp = await fetch(`/api/ai/workflows/${workflowName}/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ config })
            });
            
            const data = await resp.json();
            
            if (data.success) {
                closeModal('aiWorkflowConfigModal');
                await loadWorkflows();
                alert('Configuration saved successfully!');
            } else {
                alert(data.error || 'Failed to save configuration');
            }
        } catch (error) {
            console.error('Save config error', error);
            alert('Error saving configuration');
        }
    };

    // ========== Knowledge Base ==========
    const loadKnowledgeBase = async () => {
        if (els.knowledgeDocuments) {
            els.knowledgeDocuments.innerHTML = '<div class="py-4 text-center text-muted">Loading documents...</div>';
        }
        try {
            const resp = await fetch('/api/ai/knowledge-base');
            const data = await resp.json();
            if (data.success) {
                state.knowledgeBase = {
                    categories: data.categories || {},
                    documents: data.documents || {}
                };
                renderCategories();
                renderDocuments();
                populateCategorySelect();
            } else {
                showStatusMessage(els.knowledgeDocuments, 'No knowledge base documents yet');
            }
        } catch (error) {
            console.error('Knowledge base error', error);
            showStatusMessage(els.knowledgeDocuments, 'Failed to load knowledge base', true);
        }
    };

    const renderCategories = () => {
        if (!els.knowledgeCategories) return;
        const chips = ['all', ...Object.keys(state.knowledgeBase.categories || {})];
        if (!chips.length) {
            els.knowledgeCategories.innerHTML = '<div class="text-muted small">No categories configured</div>';
            return;
        }
        els.knowledgeCategories.innerHTML = chips.map((key) => {
            const meta = state.knowledgeBase.categories[key];
            const label = key === 'all' ? 'All Documents' : (typeof meta === 'string' ? meta : (meta?.name || key));
            return `<button class="ai-chip ${state.currentCategory === key ? 'active' : ''}" data-category="${key}">${label}</button>`;
        }).join('');
        if (els.categoryBadge) {
            const meta = state.knowledgeBase.categories[state.currentCategory];
            const label = state.currentCategory === 'all'
                ? 'All categories'
                : (typeof meta === 'string' ? meta : (meta?.name || state.currentCategory));
            els.categoryBadge.textContent = label;
        }
    };

    const collectDocuments = () => {
        const docs = [];
        Object.entries(state.knowledgeBase.documents || {}).forEach(([category, list]) => {
            if (state.currentCategory === 'all' || state.currentCategory === category) {
                (list || []).forEach((doc) => docs.push({ ...doc, category }));
            }
        });
        return docs.sort((a, b) => (b.priority || 0) - (a.priority || 0));
    };

    const renderDocuments = () => {
        if (!els.knowledgeDocuments) return;
        const docs = collectDocuments();
        if (!docs.length) {
            showStatusMessage(els.knowledgeDocuments, 'No documents found for this category');
            return;
        }
        const fragment = docs.map((doc) => `
            <div class="ai-knowledge-card mb-3">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <div class="ai-doc-title">${doc.title}</div>
                        <div class="ai-doc-meta">${doc.category} • Priority ${doc.priority || 1}</div>
                        <div class="ai-doc-length">${(doc.content || '').length} characters</div>
                    </div>
                    <div class="ai-doc-actions d-flex gap-2">
                        <button class="btn btn-light btn-sm" data-ai-view data-doc-id="${doc.id}" data-category="${doc.category}">
                            <i class="fas fa-eye me-1"></i>View
                        </button>
                        <button class="btn btn-outline-danger btn-sm" data-ai-delete data-doc-id="${doc.id}" data-category="${doc.category}">
                            <i class="fas fa-trash me-1"></i>Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        els.knowledgeDocuments.innerHTML = fragment;
    };

    const populateCategorySelect = () => {
        if (!els.docCategorySelect) return;
        const options = Object.entries(state.knowledgeBase.categories || {}).map(([key, meta]) => {
            const label = typeof meta === 'string' ? meta : (meta?.name || key);
            return `<option value="${key}">${label}</option>`;
        }).join('');
        els.docCategorySelect.innerHTML = options || '<option value="">No categories</option>';
    };

    const findDocument = (docId, category) => {
        if (category && state.knowledgeBase.documents[category]) {
            return state.knowledgeBase.documents[category].find((d) => String(d.id) === String(docId));
        }
        const flat = collectDocuments();
        return flat.find((d) => String(d.id) === String(docId));
    };

    const viewDocument = (docId, category) => {
        const doc = findDocument(docId, category);
        if (!doc) {
            alert('Document not found');
            return;
        }
        if (els.viewDocTitle) els.viewDocTitle.textContent = doc.title;
        if (els.viewDocMeta) {
            const meta = state.knowledgeBase.categories[doc.category];
            const label = typeof meta === 'string' ? meta : (meta?.name || doc.category);
            els.viewDocMeta.textContent = `${label} • Priority ${doc.priority || 1}`;
        }
        if (els.viewDocContent) els.viewDocContent.textContent = doc.content || '';
        const modal = getModal('aiViewDocumentModal');
        modal?.show();
    };

    const addDocument = async () => {
        const payload = {
            category: els.docCategorySelect?.value,
            title: document.getElementById('aiDocTitle')?.value,
            content: document.getElementById('aiDocContent')?.value,
            priority: parseInt(document.getElementById('aiDocPriority')?.value || '1', 10)
        };
        if (!payload.category || !payload.title || !payload.content) {
            alert('All fields are required.');
            return;
        }
        try {
            const resp = await fetch('/api/ai/knowledge-base', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (!data.success) {
                alert(data.error || 'Unable to add document.');
                return;
            }
            els.addDocumentForm?.reset();
            closeModal('aiAddDocumentModal');
            await loadKnowledgeBase();
        } catch (error) {
            console.error('Add document error', error);
            alert('Unable to add document.');
        }
    };

    const deleteDocument = async (docId, category) => {
        if (!confirm('Delete this document?')) return;
        try {
            const doc = findDocument(docId, category);
            const encodedCat = encodeURIComponent(doc?.category || category);
            const encodedTitle = encodeURIComponent(doc?.title || docId);
            const resp = await fetch(`/api/ai/knowledge-base/${encodedCat}/${encodedTitle}`, {
                method: 'DELETE'
            });
            const data = await resp.json();
            if (!data.success) {
                alert('Unable to delete document.');
                return;
            }
            await loadKnowledgeBase();
        } catch (error) {
            console.error('Delete document error', error);
            alert('Unable to delete document.');
        }
    };

    const copyDocumentContent = async () => {
        const text = els.viewDocContent?.textContent || '';
        if (!text) return;
        if (navigator?.clipboard?.writeText) {
            try {
                await navigator.clipboard.writeText(text);
                alert('Copied to clipboard');
                return;
            } catch (error) {
                console.warn('Clipboard API failed, falling back', error);
            }
        }
        const range = document.createRange();
        range.selectNodeContents(els.viewDocContent);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
    };

    // ========== Payment Plans ==========
    const searchMembers = async (query) => {
        try {
            const resp = await fetch(`/api/members/search?q=${encodeURIComponent(query)}&limit=10`);
            const data = await resp.json();
            if (data.success && data.members?.length) {
                els.memberSearchResults.innerHTML = data.members.map(m => `
                    <a href="#" class="list-group-item list-group-item-action" 
                       data-member-name="${m.full_name || ''}"
                       data-member-id="${m.prospect_id || m.guid || ''}"
                       data-past-due="${m.amount_past_due || 0}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${m.full_name || 'Unknown'}</strong>
                                <small class="text-muted d-block">${m.email || ''}</small>
                            </div>
                            ${m.amount_past_due > 0 ? `<span class="badge bg-danger">$${Number(m.amount_past_due).toFixed(2)} past due</span>` : ''}
                        </div>
                    </a>
                `).join('');
            } else {
                els.memberSearchResults.innerHTML = '<div class="list-group-item text-muted">No members found</div>';
            }
        } catch (error) {
            console.error('Member search error', error);
            els.memberSearchResults.innerHTML = '<div class="list-group-item text-danger">Search failed</div>';
        }
    };

    const loadPaymentPlans = async () => {
        if (!els.paymentPlansList) return;
        els.paymentPlansList.innerHTML = '<div class="py-4 text-center text-muted">Loading payment plans...</div>';
        
        try {
            const resp = await fetch('/api/ai/payment-plans');
            const data = await resp.json();
            if (data.success) {
                renderPaymentPlans(data.plans || []);
            } else {
                showStatusMessage(els.paymentPlansList, 'No payment plans yet');
            }
        } catch (error) {
            console.error('Payment plans load error', error);
            showStatusMessage(els.paymentPlansList, 'Failed to load payment plans', true);
        }
    };

    const renderPaymentPlans = (plans) => {
        if (!els.paymentPlansList) return;
        if (!plans.length) {
            showStatusMessage(els.paymentPlansList, 'No active payment plans. Click "Add Payment Plan" to create one.');
            return;
        }
        
        const html = plans.map(plan => {
            const progress = plan.installments_total > 0 
                ? ((plan.installments_paid / plan.installments_total) * 100).toFixed(0) 
                : 0;
            const statusBadge = plan.status === 'completed' 
                ? '<span class="badge bg-success">Completed</span>'
                : plan.status === 'active' 
                    ? '<span class="badge bg-primary">Active</span>'
                    : `<span class="badge bg-secondary">${plan.status}</span>`;
            
            const nextInstallment = (plan.installments || []).find(i => i.status !== 'paid');
            
            return `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <h6 class="mb-1">${plan.member_name || 'Member'}</h6>
                                <small class="text-muted">${plan.plan_name || 'Payment Plan'}</small>
                            </div>
                            ${statusBadge}
                        </div>
                        
                        <div class="row g-2 mb-3">
                            <div class="col-4 text-center">
                                <div class="small text-muted">Total</div>
                                <div class="fw-bold">$${Number(plan.total_amount || 0).toFixed(2)}</div>
                            </div>
                            <div class="col-4 text-center">
                                <div class="small text-muted">Paid</div>
                                <div class="fw-bold text-success">$${Number((plan.total_amount || 0) - (plan.balance_remaining || 0)).toFixed(2)}</div>
                            </div>
                            <div class="col-4 text-center">
                                <div class="small text-muted">Remaining</div>
                                <div class="fw-bold text-danger">$${Number(plan.balance_remaining || 0).toFixed(2)}</div>
                            </div>
                        </div>
                        
                        <div class="progress mb-2" style="height: 8px;">
                            <div class="progress-bar bg-success" style="width: ${progress}%"></div>
                        </div>
                        <small class="text-muted">${plan.installments_paid || 0} of ${plan.installments_total || 0} payments (${progress}%)</small>
                        
                        ${nextInstallment ? `
                            <div class="mt-3 p-2 bg-light rounded">
                                <small class="text-muted d-block">Next Payment Due:</small>
                                <strong>$${Number(nextInstallment.amount || 0).toFixed(2)}</strong> on ${formatShortDate(nextInstallment.due_date)}
                            </div>
                        ` : ''}
                        
                        <div class="d-flex justify-content-end gap-2 mt-3">
                            ${plan.status === 'active' && nextInstallment ? `
                                <button class="btn btn-success btn-sm" 
                                        data-member-id="${plan.member_id}"
                                        data-member-name="${plan.member_name || ''}"
                                        data-installment-id="${nextInstallment.id}"
                                        data-installment-num="${nextInstallment.installment_number}"
                                        data-amount="${nextInstallment.amount}"
                                        data-ai-record-payment>
                                    <i class="fas fa-dollar-sign me-1"></i>Record Payment
                                </button>
                            ` : ''}
                            <button class="btn btn-outline-danger btn-sm" 
                                    data-member-id="${plan.member_id}" 
                                    data-ai-remove-plan>
                                <i class="fas fa-trash me-1"></i>Remove
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        els.paymentPlansList.innerHTML = html;
    };

    const addPaymentPlan = async () => {
        const memberName = els.memberNameInput?.value?.trim();
        const totalOwed = parseFloat(document.getElementById('aiPaymentPlanTotalOwed')?.value) || 0;
        const installments = parseInt(document.getElementById('aiPaymentPlanInstallments')?.value) || 0;
        const frequency = parseInt(document.getElementById('aiPaymentPlanFrequency')?.value) || 14;
        const startDate = document.getElementById('aiPaymentPlanStartDate')?.value;
        const notes = document.getElementById('aiPaymentPlanNotes')?.value;
        
        if (!memberName) {
            alert('Please select a member by typing their name.');
            return;
        }
        if (totalOwed <= 0) {
            alert('Total amount owed must be greater than zero.');
            return;
        }
        if (installments <= 0) {
            alert('Number of payments must be at least 1.');
            return;
        }
        
        try {
            const resp = await fetch('/api/ai/payment-plans', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    member_name: memberName,
                    member_id: state.selectedMember?.id || null,
                    total_amount: totalOwed,
                    installments_total: installments,
                    frequency_days: frequency,
                    start_date: startDate,
                    notes: notes
                })
            });
            
            const data = await resp.json();
            
            if (data.success) {
                els.addPaymentPlanForm?.reset();
                state.selectedMember = null;
                closeModal('aiAddPaymentPlanModal');
                await loadPaymentPlans();
                alert('Payment plan created successfully! This member is now protected from auto-lock.');
            } else {
                alert(data.error || 'Unable to create payment plan.');
            }
        } catch (error) {
            console.error('Add payment plan error', error);
            alert('Unable to create payment plan.');
        }
    };

    const openRecordPaymentModal = (dataset) => {
        document.getElementById('aiRecordPaymentMemberId').value = dataset.memberId;
        document.getElementById('aiRecordPaymentInstallmentId').value = dataset.installmentId;
        document.getElementById('aiRecordPaymentMemberName').textContent = dataset.memberName;
        document.getElementById('aiRecordPaymentInstallmentNum').textContent = `#${dataset.installmentNum}`;
        document.getElementById('aiRecordPaymentDueAmount').textContent = `$${Number(dataset.amount).toFixed(2)}`;
        document.getElementById('aiRecordPaymentAmount').value = dataset.amount;
        document.getElementById('aiRecordPaymentDate').valueAsDate = new Date();
        openModal('aiRecordPaymentModal');
    };

    const recordPayment = async () => {
        const memberId = document.getElementById('aiRecordPaymentMemberId')?.value;
        const installmentId = document.getElementById('aiRecordPaymentInstallmentId')?.value;
        const amount = parseFloat(document.getElementById('aiRecordPaymentAmount')?.value) || 0;
        const paidDate = document.getElementById('aiRecordPaymentDate')?.value;
        
        if (!memberId || !installmentId || amount <= 0) {
            alert('Invalid payment details.');
            return;
        }
        
        try {
            const resp = await fetch(`/api/ai/payment-plans/${memberId}/payments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    installment_id: parseInt(installmentId),
                    amount_paid: amount,
                    paid_date: paidDate
                })
            });
            
            const data = await resp.json();
            
            if (data.success) {
                closeModal('aiRecordPaymentModal');
                await loadPaymentPlans();
                alert('Payment recorded successfully!');
            } else {
                alert(data.error || 'Unable to record payment.');
            }
        } catch (error) {
            console.error('Record payment error', error);
            alert('Unable to record payment.');
        }
    };

    const removePlan = async (memberId) => {
        if (!confirm('Remove this payment plan? The member will no longer be protected from auto-lock.')) return;
        
        try {
            const resp = await fetch(`/api/ai/payment-plans/${encodeURIComponent(memberId)}`, {
                method: 'DELETE'
            });
            
            const data = await resp.json();
            
            if (data.success) {
                await loadPaymentPlans();
                alert('Payment plan removed.');
            } else {
                alert(data.error || 'Unable to remove payment plan.');
            }
        } catch (error) {
            console.error('Remove plan error', error);
            alert('Unable to remove payment plan.');
        }
    };

    // ========== Utilities ==========
    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        if (Number.isNaN(date.getTime())) return dateStr;
        return date.toLocaleString();
    };

    const formatShortDate = (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        if (Number.isNaN(date.getTime())) return dateStr;
        return date.toLocaleDateString();
    };

    init();
})(window);
