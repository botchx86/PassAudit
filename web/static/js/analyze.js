// PassAudit - Analyze Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Single Password Analysis
    const singlePasswordInput = document.getElementById('single-password');
    const singleShowCheckbox = document.getElementById('single-show');
    const singleHibpCheckbox = document.getElementById('single-hibp');
    const analyzeSingleBtn = document.getElementById('analyze-single-btn');
    const singleResultDiv = document.getElementById('single-result');

    // Batch Analysis
    const batchFileInput = document.getElementById('batch-file');
    const batchHibpCheckbox = document.getElementById('batch-hibp');
    const analyzeBatchBtn = document.getElementById('analyze-batch-btn');
    const batchResultDiv = document.getElementById('batch-result');

    // Password Generation
    const genCountInput = document.getElementById('gen-count');
    const genLengthInput = document.getElementById('gen-length');
    const genUppercaseCheckbox = document.getElementById('gen-uppercase');
    const genLowercaseCheckbox = document.getElementById('gen-lowercase');
    const genDigitsCheckbox = document.getElementById('gen-digits');
    const genSymbolsCheckbox = document.getElementById('gen-symbols');
    const generateBtn = document.getElementById('generate-btn');
    const generateResultDiv = document.getElementById('generate-result');

    // Single Password: Toggle visibility
    if (singleShowCheckbox) {
        singleShowCheckbox.addEventListener('change', function() {
            singlePasswordInput.type = this.checked ? 'text' : 'password';
        });
    }

    // Single Password: Analyze
    if (analyzeSingleBtn) {
        analyzeSingleBtn.addEventListener('click', function() {
            const password = singlePasswordInput.value;

            if (!password) {
                PassAudit.showAlert(singleResultDiv.parentElement, 'Please enter a password', 'warning');
                return;
            }

            PassAudit.showLoading(analyzeSingleBtn);
            singleResultDiv.style.display = 'none';

            const requestData = {
                password: password,
                check_hibp: singleHibpCheckbox.checked
            };

            fetch('/analyze/single', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                PassAudit.hideLoading(analyzeSingleBtn);

                if (data.error) {
                    PassAudit.showAlert(singleResultDiv.parentElement, data.error, 'danger');
                    return;
                }

                displaySingleResult(data);
            })
            .catch(error => {
                PassAudit.hideLoading(analyzeSingleBtn);
                PassAudit.showAlert(singleResultDiv.parentElement, 'Error: ' + error, 'danger');
            });
        });
    }

    // Batch Analysis
    if (analyzeBatchBtn) {
        analyzeBatchBtn.addEventListener('click', function() {
            const file = batchFileInput.files[0];

            if (!file) {
                PassAudit.showAlert(batchResultDiv.parentElement, 'Please select a file', 'warning');
                return;
            }

            PassAudit.showLoading(analyzeBatchBtn);
            batchResultDiv.style.display = 'none';

            const formData = new FormData();
            formData.append('file', file);
            formData.append('check_hibp', batchHibpCheckbox.checked);

            fetch('/analyze/batch', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                PassAudit.hideLoading(analyzeBatchBtn);

                if (data.error) {
                    PassAudit.showAlert(batchResultDiv.parentElement, data.error, 'danger');
                    return;
                }

                displayBatchResult(data);
            })
            .catch(error => {
                PassAudit.hideLoading(analyzeBatchBtn);
                PassAudit.showAlert(batchResultDiv.parentElement, 'Error: ' + error, 'danger');
            });
        });
    }

    // Password Generation
    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            const count = parseInt(genCountInput.value) || 5;
            const length = parseInt(genLengthInput.value) || 16;

            if (!genUppercaseCheckbox.checked && !genLowercaseCheckbox.checked &&
                !genDigitsCheckbox.checked && !genSymbolsCheckbox.checked) {
                PassAudit.showAlert(generateResultDiv.parentElement,
                    'Please select at least one character type', 'warning');
                return;
            }

            PassAudit.showLoading(generateBtn);
            generateResultDiv.style.display = 'none';

            const requestData = {
                count: count,
                length: length,
                use_uppercase: genUppercaseCheckbox.checked,
                use_lowercase: genLowercaseCheckbox.checked,
                use_digits: genDigitsCheckbox.checked,
                use_symbols: genSymbolsCheckbox.checked
            };

            fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                PassAudit.hideLoading(generateBtn);

                if (data.error) {
                    PassAudit.showAlert(generateResultDiv.parentElement, data.error, 'danger');
                    return;
                }

                displayGeneratedPasswords(data);
            })
            .catch(error => {
                PassAudit.hideLoading(generateBtn);
                PassAudit.showAlert(generateResultDiv.parentElement, 'Error: ' + error, 'danger');
            });
        });
    }

    // Display functions
    function displaySingleResult(data) {
        const score = data.strength_score;
        const progressBarClass = PassAudit.getProgressBarClass(score);
        const strengthBadge = PassAudit.getStrengthBadge(score);

        let html = `
            <div class="alert alert-success">
                <i class="bi bi-check-circle-fill"></i> Analysis complete
            </div>

            <div class="mb-3">
                <label class="form-label fw-bold">Strength Score:</label>
                <div class="progress" style="height: 30px;">
                    <div class="progress-bar ${progressBarClass}" role="progressbar"
                         style="width: ${score}%;" aria-valuenow="${score}">
                        <span class="fw-bold">${score}/100</span>
                    </div>
                </div>
                <div class="mt-2 text-center">${strengthBadge}</div>
            </div>

            <div class="row mb-3">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h6 class="text-muted">Length</h6>
                            <p class="fs-4 mb-0">${data.length}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h6 class="text-muted">Entropy</h6>
                            <p class="fs-4 mb-0">${data.entropy} bits</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h6 class="text-muted">Common</h6>
                            <p class="fs-4 mb-0">${data.is_common ? '<span class="text-danger">YES</span>' : '<span class="text-success">NO</span>'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (data.hibp_pwned !== undefined) {
            const hibpClass = data.hibp_pwned ? 'danger' : 'success';
            const hibpIcon = data.hibp_pwned ? 'exclamation-triangle-fill' : 'check-circle-fill';
            const hibpText = data.hibp_pwned ?
                `Found in ${data.hibp_count.toLocaleString()} breaches!` : 'Not found in breaches';

            html += `
                <div class="alert alert-${hibpClass}">
                    <i class="bi bi-${hibpIcon}"></i> <strong>HIBP Check:</strong> ${hibpText}
                </div>
            `;
        }

        if (Object.keys(data.patterns).length > 0) {
            html += '<h6 class="mb-2"><i class="bi bi-bug-fill text-warning"></i> Detected Patterns:</h6><div class="mb-3">';
            for (const [type, items] of Object.entries(data.patterns)) {
                html += `<span class="badge bg-warning me-2 mb-2">${type.replace(/_/g, ' ')}</span>`;
            }
            html += '</div>';
        }

        if (data.feedback && data.feedback.length > 0) {
            html += '<h6 class="mb-2"><i class="bi bi-lightbulb-fill text-info"></i> Recommendations:</h6><ul>';
            data.feedback.forEach(item => {
                html += `<li>${item}</li>`;
            });
            html += '</ul>';
        }

        singleResultDiv.innerHTML = html;
        singleResultDiv.style.display = 'block';
    }

    function displayBatchResult(data) {
        const summary = data.summary;

        let html = `
            <div class="alert alert-success">
                <i class="bi bi-check-circle-fill"></i>
                Analyzed ${data.total} passwords successfully
            </div>

            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">Summary Statistics</h5>
                    <div class="row">
                        <div class="col-md-3">
                            <p class="mb-1 text-muted">Average Score</p>
                            <p class="fs-4 mb-0">${summary.average_score}/100</p>
                        </div>
                        <div class="col-md-3">
                            <p class="mb-1 text-muted">Weak Passwords</p>
                            <p class="fs-4 mb-0">${summary.weak_count}</p>
                        </div>
                        <div class="col-md-3">
                            <p class="mb-1 text-muted">Common Passwords</p>
                            <p class="fs-4 mb-0">${summary.common_count}</p>
                        </div>
                        ${summary.breached_count !== undefined ? `
                        <div class="col-md-3">
                            <p class="mb-1 text-muted">Breached</p>
                            <p class="fs-4 mb-0 text-danger">${summary.breached_count}</p>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Strength Distribution</h5>
                    <div class="mb-2">
                        <small>Very Strong:</small>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-success" style="width: ${summary.strength_distribution.very_strong / data.total * 100}%">
                                ${summary.strength_distribution.very_strong}
                            </div>
                        </div>
                    </div>
                    <div class="mb-2">
                        <small>Strong:</small>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-info" style="width: ${summary.strength_distribution.strong / data.total * 100}%">
                                ${summary.strength_distribution.strong}
                            </div>
                        </div>
                    </div>
                    <div class="mb-2">
                        <small>Medium:</small>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-warning" style="width: ${summary.strength_distribution.medium / data.total * 100}%">
                                ${summary.strength_distribution.medium}
                            </div>
                        </div>
                    </div>
                    <div class="mb-2">
                        <small>Weak:</small>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-orange" style="width: ${summary.strength_distribution.weak / data.total * 100}%">
                                ${summary.strength_distribution.weak}
                            </div>
                        </div>
                    </div>
                    <div class="mb-2">
                        <small>Very Weak:</small>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-danger" style="width: ${summary.strength_distribution.very_weak / data.total * 100}%">
                                ${summary.strength_distribution.very_weak}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        batchResultDiv.innerHTML = html;
        batchResultDiv.style.display = 'block';
    }

    function displayGeneratedPasswords(data) {
        let html = `
            <div class="alert alert-success">
                <i class="bi bi-check-circle-fill"></i>
                Generated ${data.count} password(s)
            </div>

            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Password</th>
                            <th>Strength</th>
                            <th>Entropy</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        data.passwords.forEach((item, index) => {
            const strengthBadge = PassAudit.getStrengthBadge(item.strength_score);
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><code>${item.password}</code></td>
                    <td>${strengthBadge}<br><small>${item.strength_score}/100</small></td>
                    <td>${item.entropy} bits</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary copy-btn" data-password="${item.password}">
                            <i class="bi bi-clipboard"></i> Copy
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        generateResultDiv.innerHTML = html;
        generateResultDiv.style.display = 'block';

        // Add copy functionality
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const password = this.dataset.password;
                PassAudit.copyToClipboard(password);
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    }
});
