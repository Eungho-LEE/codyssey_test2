(function () {
  'use strict';
  function legacyCopy(text) {
    const input = document.createElement('textarea');
    input.value = text;
    input.setAttribute('readonly', '');
    input.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:0';
    document.body.append(input);
    input.focus();
    input.select();
    let success = false;
    try { success = document.execCommand('copy'); } catch (_) {}
    input.remove();
    return success;
  }
  document.querySelectorAll('pre > code').forEach((code, index) => {
    const pre = code.parentElement;
    let bar = pre.previousElementSibling;
    if (!bar || !bar.classList.contains('code-label')) return;
    // Exported workbook HTML may already contain the controls. Bind each page load once.
    let button = bar.querySelector('[data-copy-code]');
    let status = bar.querySelector('.code-copy-status');
    if (!button) {
      const label = document.createElement('span');
      label.className = 'code-language';
      label.textContent = bar.textContent;
      bar.replaceChildren(label);
      const actions = document.createElement('span');
      actions.className = 'code-copy-actions';
      status = document.createElement('span');
      status.className = 'code-copy-status';
      status.setAttribute('role', 'status');
      status.setAttribute('aria-live', 'polite');
      button = document.createElement('button');
      button.type = 'button';
      button.dataset.copyCode = String(index);
      button.textContent = '코드 복사';
      button.setAttribute('aria-label', '이 코드 블록 전체 복사');
      actions.append(status, button);
      bar.append(actions);
    }
    status.textContent = '';
    button.disabled = false;
    button.addEventListener('click', async () => {
      button.disabled = true;
      status.textContent = '';
      const text = code.textContent;
      let copied = false;
      try {
        if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
          await navigator.clipboard.writeText(text);
          copied = true;
        }
      } catch (_) { /* Local files or denied clipboard permission: use the fallback. */ }
      if (!copied) copied = legacyCopy(text);
      button.disabled = false;
      button.focus({ preventScroll: true });
      if (copied) {
        status.textContent = '복사 완료';
      } else {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(code);
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent = '코드가 선택됐습니다. Ctrl+C로 복사하세요.';
      }
    });
  });
}());
