function fsAddClass(el, name) {
    if (el.classList.contains(name)) return;
    el.classList.add(name);
}

function fsWrapGroup(control) {
    if (control.closest('.form-group')) return null;
    const group = document.createElement('div');
    group.className = 'form-group';
    const parent = control.parentNode;
    if (!parent) return null;
    parent.insertBefore(group, control);
    group.appendChild(control);
    return group;
}

function fsLabelFor(control) {
    const group = control.closest('.form-group');
    if (!group) return null;
    let label = group.querySelector('label');
    if (!label) {
        label = document.createElement('label');
        group.insertBefore(label, control);
    }
    if (!label.getAttribute('for')) label.setAttribute('for', control.id);
    return label;
}

function fsNormalizeControl(control) {
    if (control.type === 'hidden') {
        fsAddClass(control, 'form-control');
        return;
    }
    if (control.type === 'checkbox' || control.type === 'radio') {
        fsAddClass(control, 'form-check');
        return;
    }
    fsAddClass(control, 'form-control');
    const group = fsWrapGroup(control);
    if (!group) return;
    const label = fsLabelFor(control);
    if (control.required && label && !label.querySelector('.req')) {
        const mark = document.createElement('span');
        mark.className = 'req';
        mark.textContent = '*';
        mark.title = 'Obligatorio';
        label.appendChild(mark);
    }
}

function fsFindForms(root) {
    const scope = root || document;
    return Array.from(scope.querySelectorAll('form'));
}

function fsNormalizeForm(form) {
    fsAddClass(form, 'fs-form');
    Array.from(form.querySelectorAll('input, select, textarea')).forEach(fsNormalizeControl);
    fsWrapActions(form);
    fsEnhancePasswords(form);
}

function fsWrapActions(form) {
    if (form.querySelector('.form-actions')) return;
    const buttons = Array.from(form.querySelectorAll('button[type="submit"], button:not([type])'));
    if (buttons.length === 0) return;
    const hasCancel = buttons.some(b => b.dataset && b.dataset.cancel === 'true');
    const primary = buttons.find(b => {
        const cls = b.className || '';
        return !hasCancel || cls.indexOf('btn-primary') !== -1;
    }) || buttons[0];
    if (!primary || primary.closest('.form-actions')) return;
    const actions = document.createElement('div');
    actions.className = 'form-actions';
    primary.parentNode.insertBefore(actions, primary);
    if (hasCancel) {
        const cancel = buttons.find(b => b !== primary);
        if (cancel) {
            cancel.dataset.cancel = 'true';
            actions.appendChild(cancel);
        }
    }
    actions.appendChild(primary);
}

function fsEnhancePasswords(form) {
    Array.from(form.querySelectorAll('input[type="password"]')).forEach(pw => {
        if (pw.dataset.pwEnhanced === 'true') return;
        pw.dataset.pwEnhanced = 'true';
        pw.classList.add('toggle-password');
        if (!pw.parentNode || !pw.parentNode.classList.contains('input-wrapper')) {
            const wrap = document.createElement('div');
            wrap.className = 'input-wrapper';
            pw.parentNode.insertBefore(wrap, pw);
            wrap.appendChild(pw);
        }
        if (pw.parentNode.querySelector('.toggle-password-btn')) return;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'toggle-password-btn';
        btn.setAttribute('aria-label', 'Mostrar contraseña');
        btn.innerHTML = '<i class="fas fa-eye"></i>';
        btn.addEventListener('click', () => {
            const isText = pw.type === 'text';
            pw.type = isText ? 'password' : 'text';
            btn.innerHTML = isText ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
            btn.setAttribute('aria-label', isText ? 'Mostrar contraseña' : 'Ocultar contraseña');
        });
        pw.parentNode.appendChild(btn);
    });
}

function fsSetLoading(form, loading) {
    const buttons = Array.from(form.querySelectorAll('.form-actions button, button[type="submit"]'));
    buttons.forEach(b => {
        if (b.dataset && b.dataset.cancel === 'true') return;
        b.classList.toggle('is-loading', loading);
        b.disabled = loading;
    });
}

function fsClearValidation(form) {
    Array.from(form.querySelectorAll('.form-control')).forEach(el => el.classList.remove('is-invalid'));
    Array.from(form.querySelectorAll('.form-hint')).forEach(h => {
        if (h.dataset.originalText) h.textContent = h.dataset.originalText;
        h.classList.remove('error', 'success');
    });
}

function fsValidate(form) {
    fsClearValidation(form);
    let firstInvalid = null;
    Array.from(form.querySelectorAll('input, select, textarea')).forEach(control => {
        if (control.type === 'hidden' || !control.required) return;
        const value = (control.value || '').trim();
        if (value !== '') {
            control.classList.remove('is-invalid');
            return;
        }
        control.classList.add('is-invalid');
        if (!firstInvalid) firstInvalid = control;
    });
    return firstInvalid;
}

function fsGuardForm(form) {
    if (form.dataset.fsGuarded === 'true') return;
    form.dataset.fsGuarded = 'true';
    form.addEventListener('submit', () => {
        const firstInvalid = fsValidate(form);
        if (firstInvalid) {
            fsSetLoading(form, false);
            firstInvalid.focus();
        }
    }, true);
    Array.from(form.querySelectorAll('input, select, textarea')).forEach(control => {
        const clear = () => control.classList.remove('is-invalid');
        control.addEventListener('input', clear);
        control.addEventListener('change', clear);
    });
}

function fsValidateEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
}

function fsValidateUsername(value) {
    return /^[A-Za-z0-9._-]{3,30}$/.test(value);
}

function fsFieldError(id, message) {
    const control = document.getElementById(id);
    if (!control) return false;
    control.classList.add('is-invalid');
    const group = control.closest('.form-group');
    if (group) {
        let hint = group.querySelector('.form-hint');
        if (!hint) {
            hint = document.createElement('small');
            hint.className = 'form-hint';
            group.appendChild(hint);
        }
        if (!hint.dataset.originalText) hint.dataset.originalText = hint.textContent || '';
        hint.textContent = message;
        hint.classList.add('error');
        hint.classList.remove('success');
    }
    return false;
}

function fsClearField(id) {
    const control = document.getElementById(id);
    if (!control) return;
    control.classList.remove('is-invalid');
    const group = control.closest('.form-group');
    if (group) {
        const hint = group.querySelector('.form-hint');
        if (hint) {
            hint.textContent = hint.dataset.originalText || '';
            hint.classList.remove('error', 'success');
        }
    }
}

function fsValidateFormFields(formId, rules) {
    const form = document.getElementById(formId);
    if (form) fsClearValidation(form);
    let ok = true;
    for (const id in rules) {
        if (!rules.hasOwnProperty(id)) continue;
        const control = document.getElementById(id);
        if (!control) continue;
        const value = (control.value || '').trim();
        const rule = rules[id];
        if (rule.required && value === '') {
            ok = fsFieldError(id, rule.requiredMessage || 'Este campo es obligatorio');
            continue;
        }
        if (value !== '' && rule.email && !fsValidateEmail(value)) {
            ok = fsFieldError(id, 'Formato de correo no válido');
            continue;
        }
        if (value !== '' && rule.username && !fsValidateUsername(value)) {
            ok = fsFieldError(id, 'Solo letras, números, punto, guion y guion bajo (mín. 3)');
            continue;
        }
        if (value !== '' && rule.minLength && value.length < rule.minLength) {
            ok = fsFieldError(id, `Mínimo ${rule.minLength} caracteres`);
            continue;
        }
        fsClearField(id);
    }
    if (!ok) {
        const firstBad = document.querySelector('#' + formId + ' .is-invalid');
        if (firstBad) firstBad.focus();
    }
    return ok;
}

function initFormStandard() {
    const forms = fsFindForms();
    if (forms.length === 0) return;
    forms.forEach(form => {
        fsNormalizeForm(form);
        fsGuardForm(form);
    });
}

document.addEventListener('DOMContentLoaded', initFormStandard);
