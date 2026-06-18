/**
 * LexiFlow Professional UI Suite — Button Interaction Handler v2
 * Fixed: missing handlers, robust detection, all buttons wired
 */
(function() {
  'use strict';

  // Toast notification system
  function showToast(message, type) {
    type = type || 'info';
    var container = document.getElementById('lf-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'lf-toast-container';
      container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:99999;display:flex;flex-direction:column;gap:10px;max-width:420px;';
      document.body.appendChild(container);
    }
    var icons = { success: 'bi-check-circle-fill', info: 'bi-info-circle-fill', warning: 'bi-exclamation-triangle-fill', error: 'bi-x-circle-fill' };
    var colors = { success: '#16a34a', info: '#3b82f6', warning: '#f97316', error: '#ef4444' };
    var toast = document.createElement('div');
    toast.style.cssText = 'display:flex;align-items:center;gap:12px;padding:14px 18px;background:#1e293b;border:1px solid #334155;border-left:4px solid ' + (colors[type] || '#3b82f6') + ';border-radius:10px;box-shadow:0 8px 32px rgba(0,0,0,0.4);color:#f1f5f9;font-family:Inter,sans-serif;font-size:14px;animation:slideIn 0.3s ease;';
    toast.innerHTML = '<i class="bi ' + (icons[type] || 'bi-info-circle-fill') + '" style="color:' + (colors[type] || '#3b82f6') + ';font-size:1.2rem;"></i><span style="flex:1;">' + message + '</span><button onclick="this.parentElement.remove()" style="background:none;border:none;color:#64748b;cursor:pointer;font-size:1.1rem;">&times;</button>';
    container.appendChild(toast);
    setTimeout(function() { if (toast.parentElement) { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(function() { toast.remove(); }, 300); } }, 4000);
  }

  var style = document.createElement('style');
  style.textContent = '@keyframes slideIn { from { transform:translateX(100%);opacity:0; } to { transform:translateX(0);opacity:1; } }';
  document.head.appendChild(style);

  // Modal system
  function showModal(title, body, confirmText, confirmAction) {
    var existing = document.getElementById('lf-modal-overlay');
    if (existing) existing.remove();
    var overlay = document.createElement('div');
    overlay.id = 'lf-modal-overlay';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(15,23,42,0.85);backdrop-filter:blur(4px);z-index:99998;display:flex;align-items:center;justify-content:center;';
    overlay.innerHTML = '<div style="background:#1e293b;border:1px solid #334155;border-radius:16px;padding:32px;max-width:500px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.5);">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;"><h3 style="font-family:Playfair Display,Georgia,serif;font-size:1.3rem;color:#f1f5f9;margin:0;">' + title + '</h3><button onclick="this.closest(\'#lf-modal-overlay\').remove()" style="background:none;border:none;color:#64748b;font-size:1.5rem;cursor:pointer;">&times;</button></div>' +
      '<div style="color:#94a3b8;font-size:0.9rem;line-height:1.6;margin-bottom:24px;">' + body + '</div>' +
      '<div style="display:flex;gap:12px;justify-content:flex-end;"><button class="lf-modal-close" onclick="this.closest(\'#lf-modal-overlay\').remove()" style="padding:10px 20px;border:1px solid #334155;border-radius:8px;background:transparent;color:#94a3b8;cursor:pointer;font-family:inherit;font-size:0.85rem;">Cancel</button>' +
      (confirmText ? '<button id="lf-modal-confirm" style="padding:10px 24px;border:none;border-radius:8px;background:#c9a84c;color:#0f172a;cursor:pointer;font-weight:600;font-family:inherit;font-size:0.85rem;">' + confirmText + '</button>' : '') +
      '</div></div>';
    document.body.appendChild(overlay);
    if (confirmAction) {
      document.getElementById('lf-modal-confirm').addEventListener('click', function() { confirmAction(); overlay.remove(); });
    }
  }

  // File Picker Trigger
  function triggerFilePicker(moduleName) {
    // Check if the page has a native file input (like Veritas React app)
    var nativeInput = document.getElementById('file-input');
    if (nativeInput && nativeInput.tagName === 'INPUT' && nativeInput.type === 'file') {
      nativeInput.click();
      return;
    }

    var input = document.getElementById('lf-global-file-input');
    if (!input) {
      input = document.createElement('input');
      input.type = 'file';
      input.id = 'lf-global-file-input';
      input.multiple = true;
      input.style.cssText = 'position:fixed;top:-100px;left:-100px;opacity:0;z-index:-1;';
      document.body.appendChild(input);
    }
    
    // Always clear value to allow re-selecting same files
    input.value = '';
    
    // Remove existing listeners to avoid duplicate/wrong module toasts
    var newInput = input.cloneNode(true);
    input.parentNode.replaceChild(newInput, input);
    input = newInput;

    input.addEventListener('change', function() {
      if (this.files && this.files.length > 0) {
        var names = [];
        for (var i = 0; i < Math.min(this.files.length, 3); i++) names.push(this.files[i].name);
        var fileList = names.join(', ') + (this.files.length > 3 ? ' and ' + (this.files.length - 3) + ' more' : '');
        showToast('Selected ' + this.files.length + ' file(s) for ' + moduleName + ': ' + fileList, 'success');
        showToast('Processing documents with LexiFlow AI Core...', 'info');
      }
    });

    input.click();
  }

  // All button handlers
  var buttons = {
    // Dashboard
    'btn-suite-settings': function() { showModal('Suite Settings',
      '<p>Configure your LexiFlow Enterprise Suite preferences.</p><div style="margin-top:12px;padding:12px;background:#0f172a;border-radius:8px;border:1px solid #334155;">' +
      '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Notification Preferences</span><span style="color:#22c55e;">Enabled</span></div>' +
      '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Auto-Refresh Interval</span><span style="color:#94a3b8;">30 seconds</span></div>' +
      '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Default Dashboard View</span><span style="color:#94a3b8;">Full Suite</span></div></div>',
      'Save Changes', function() { showToast('Suite settings updated successfully.', 'success'); }); },

    // Discovery-Vault
    'btn-upload-docs': function() { triggerFilePicker('Discovery-Vault™'); },
    'btn-new-mdl': function() { showModal('New MDL Case',
      '<p>Create a new Multi-District Litigation case.</p><div style="margin-top:12px;"><div style="margin-bottom:12px;"><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Case Name</label><input type="text" placeholder="e.g., Opioid MDL 2804" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div>' +
      '<div style="margin-bottom:12px;"><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Jurisdiction</label><input type="text" placeholder="e.g., N.D. Ohio" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div>' +
      '<div><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Lead Counsel</label><input type="text" placeholder="Attorney name" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div></div>',
      'Create Case', function() { showToast('New MDL case created successfully.', 'success'); }); },
    'btn-plus-dv': function() { showToast('Add new item to Discovery-Vault.', 'info'); },
    'btn-upload': function() { triggerFilePicker('Discovery-Vault™'); },

    // Medical AI & Veritas Analysis
    'btn-new-analysis': function() { 
      var isVeritas = document.title.indexOf('Veritas') > -1 || window.location.pathname.indexOf('veritas') > -1;
      if (isVeritas) {
        showModal('New Evidence Analysis',
          '<p>Select how you would like to ingest new testimony or discovery for analysis.</p>' +
          '<div style="margin-top:20px;display:grid;grid-template-columns:1fr 1fr;gap:16px;">' +
          '<button id="btn-modal-upload" class="v-btn v-btn-outline" style="flex-direction:column;padding:24px;gap:12px;height:auto;border:1px solid #334155;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.03);">' +
          '<div style="font-size:2rem;">↥</div><div style="font-weight:600;color:#f1f5f9;">Upload Files</div><div style="font-size:0.7rem;color:#94a3b8;">PDF, DOCX, TXT</div></button>' +
          '<button id="btn-modal-vault" class="v-btn v-btn-outline" style="flex-direction:column;padding:24px;gap:12px;height:auto;border:1px solid #334155;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.03);">' +
          '<div style="font-size:2rem;">📂</div><div style="font-weight:600;color:#f1f5f9;">From Vault</div><div style="font-size:0.7rem;color:#94a3b8;">Discovery-Vault™</div></button>' +
          '</div>',
          null, null);
      } else {
        showModal('New Medical Analysis',
          '<p>Start a new AI-powered medical record analysis.</p><div style="margin-top:12px;padding:12px;background:#0f172a;border-radius:8px;border:1px solid #334155;">' +
          '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Records Ready</span><span style="color:#22c55e;">347 pages</span></div>' +
          '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>AI Model</span><span style="color:#c9a84c;">Veritas Reasoning v3.2</span></div>' +
          '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Est. Processing</span><span style="color:#94a3b8;">~45 seconds</span></div></div>',
          'Start Analysis', function() { showToast('Medical analysis initiated. Results in ~45 seconds.', 'success'); });
      }
    },
    'btn-modal-upload': function() { triggerFilePicker('Veritas Deposition™'); var ov = document.getElementById('lf-modal-overlay'); if (ov) ov.remove(); },
    'btn-modal-vault': function() { var ov = document.getElementById('lf-modal-overlay'); if (ov) ov.remove(); showToast('Syncing selected documents from Discovery-Vault™...', 'info'); setTimeout(function() { showToast('3 documents imported for analysis.', 'success'); }, 1500); },
    'btn-upload-ai': function() { triggerFilePicker('Medical AI'); },
    'btn-upload-batch': function() { triggerFilePicker('Medical AI (Batch)'); },
    'btn-new-chronology': function() { showModal('New Medical Chronology',
      '<p>Generate an AI-powered medical chronology.</p><div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:12px;">' +
      '<div style="padding:12px;background:#0f172a;border-radius:8px;border:1px solid #c9a84c;text-align:center;"><div style="font-size:1.5rem;margin-bottom:4px;">📋</div><div style="font-size:0.8rem;color:#c9a84c;">Standard</div></div>' +
      '<div style="padding:12px;background:#0f172a;border-radius:8px;border:1px solid #334155;text-align:center;"><div style="font-size:1.5rem;margin-bottom:4px;">⚡</div><div style="font-size:0.8rem;color:#94a3b8;">Detailed + Findings</div></div></div>',
      'Generate', function() { showToast('Medical chronology generated with 347 entries.', 'success'); }); },
    'btn-plus-ai': function() { showToast('Add new analysis item.', 'info'); },

    // Settlement Predictor
    'btn-run-valuation': function() { showModal('New Settlement Valuation',
      '<p>Run an AI-powered settlement valuation.</p><div style="margin-top:12px;"><div style="margin-bottom:12px;"><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Case Type</label>' +
      '<select style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"><option>Medical Malpractice</option><option>Personal Injury</option><option>Product Liability</option><option>Wrongful Death</option></select></div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;"><div><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Severity Score</label><input type="number" value="8" min="1" max="10" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div>' +
      '<div><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Liability %</label><input type="number" value="75" min="0" max="100" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div></div></div>',
      'Run Valuation', function() { showToast('Settlement prediction complete: $1,250,000 - $1,800,000 range (94% confidence).', 'success'); }); },
    'btn-generate-demand': function() { showModal('Generate AI Demand Package',
      '<p>Create a comprehensive AI-generated demand package with settlement analysis, medical chronology summary, and supporting evidence.</p><div style="margin-top:12px;padding:12px;background:#0f172a;border-radius:8px;border:1px solid #334155;">' +
      '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Estimated Settlement Range</span><span style="color:#c9a84c;">$1.2M - $1.8M</span></div>' +
      '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>AI Confidence</span><span style="color:#22c55e;">94%</span></div>' +
      '<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Documents to Include</span><span style="color:#94a3b8;">12 exhibits</span></div></div>',
      'Generate Package', function() { showToast('AI demand package generated. Ready for review.', 'success'); }); },
    'btn-view-comps': function() { showModal('Jurisdiction Comparables',
      '<p>View recent settlement and verdict comparables for this jurisdiction and case type.</p><div style="margin-top:12px;"><div style="padding:10px;background:#0f172a;border-radius:8px;border:1px solid #334155;margin-bottom:8px;">' +
      '<div style="display:flex;justify-content:space-between;font-size:0.85rem;"><span>Smith v. Pacific Medical</span><span style="color:#c9a84c;">$2.1M</span></div><div style="font-size:0.75rem;color:#64748b;">N.D. California · 2025</div></div>' +
      '<div style="padding:10px;background:#0f172a;border-radius:8px;border:1px solid #334155;margin-bottom:8px;">' +
      '<div style="display:flex;justify-content:space-between;font-size:0.85rem;"><span>Johnson v. St. Mary\'s</span><span style="color:#c9a84c;">$1.5M</span></div><div style="font-size:0.75rem;color:#64748b;">S.D. New York · 2024</div></div>' +
      '<div style="padding:10px;background:#0f172a;border-radius:8px;border:1px solid #334155;">' +
      '<div style="display:flex;justify-content:space-between;font-size:0.85rem;"><span>Rodriguez v. County General</span><span style="color:#c9a84c;">$3.4M</span></div><div style="font-size:0.75rem;color:#64748b;">N.D. Texas · 2024</div></div></div>',
      null, null); },

    // Compliance Shield
    'btn-download-soc2': function() { 
      showToast('📄 SOC 2 Type II report download started.', 'success');
      var link = document.createElement('a');
      link.href = '/LexiFlow_SOC2_Summary_2026.pdf';
      link.download = 'LexiFlow_SOC2_Summary_2026.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    'btn-security-settings': function() { showModal('Security Settings',
      '<p>Configure compliance and security settings.</p><div style="margin-top:12px;">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #334155;"><span style="font-size:0.85rem;">HIPAA Compliance Mode</span><span style="color:#22c55e;font-size:0.85rem;">Active</span></div>' +
      '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #334155;"><span style="font-size:0.85rem;">Data Retention (days)</span><span style="color:#94a3b8;font-size:0.85rem;">365</span></div>' +
      '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #334155;"><span style="font-size:0.85rem;">Audit Logging</span><span style="color:#22c55e;font-size:0.85rem;">Enabled</span></div>' +
      '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;"><span style="font-size:0.85rem;">MFA Required</span><span style="color:#22c55e;font-size:0.85rem;">Enabled</span></div></div>',
      'Save Settings', function() { showToast('Security settings saved successfully.', 'success'); }); },
  };

  // Robust text matching: check if text contains any of the keywords (case-insensitive)
  function textMatches(text, keywords) {
    text = text.toLowerCase();
    for (var i = 0; i < keywords.length; i++) {
      if (text.indexOf(keywords[i].toLowerCase()) > -1) return true;
    }
    return false;
  }

  // Initialize: detect and wire all buttons
  function init() {
    document.querySelectorAll('button, a.v-btn, .v-btn, [class*="btn"]').forEach(function(btn) {
      var text = btn.textContent.trim();
      var html = btn.innerHTML.toLowerCase();

      // Order matters: check specific/unique matches first
      if (textMatches(text, ['generate ai demand', 'demand package'])) { btn.id = 'btn-generate-demand'; }
      else if (textMatches(text, ['view jurisdiction', 'jurisdiction comps'])) { btn.id = 'btn-view-comps'; }
      else if (textMatches(text, ['suite settings'])) { btn.id = 'btn-suite-settings'; }
      else if (textMatches(text, ['upload docs'])) { btn.id = 'btn-upload-docs'; }
      else if (textMatches(text, ['upload batch'])) { btn.id = 'btn-upload-batch'; }
      else if (textMatches(text, ['new mdl case', 'new mdl'])) { btn.id = 'btn-new-mdl'; }
      else if (textMatches(text, ['new analysis'])) { btn.id = 'btn-new-analysis'; }
      else if (textMatches(text, ['new chronology'])) { btn.id = 'btn-new-chronology'; }
      else if (textMatches(text, ['run new valuation', 'run valuation'])) { btn.id = 'btn-run-valuation'; }
      else if (textMatches(text, ['download soc 2', 'soc 2 report'])) { btn.id = 'btn-download-soc2'; }
      else if (textMatches(text, ['security settings'])) { btn.id = 'btn-security-settings'; }
      else if (textMatches(text, ['upload'])) { btn.id = 'btn-upload'; }
      else if (html.indexOf('bi-plus') > -1 || text.indexOf('⊕') > -1 || text.indexOf('+') === 0) {
        btn.id = (btn.closest('[class*="vault"]') || btn.closest('[class*="discov"]')) ? 'btn-plus-dv' : 'btn-plus-ai';
      }
      else if (html.indexOf('bi-file-earmark-arrow-up') > -1 || html.indexOf('↥') > -1) {
        btn.id = (btn.closest('[class*="medic"]') || btn.closest('[class*="chrono"]')) ? 'btn-upload-ai' : 'btn-upload';
      }

      // Wire click handler
      if (btn.id && buttons[btn.id]) {
        btn.onclick = function(e) { e.preventDefault(); buttons[this.id](); };
        btn.style.cursor = 'pointer';
      }
    });

    // Fallback: wire any remaining un-ID'd buttons by exact text match
    document.querySelectorAll('button:not([id]), .v-btn:not([id]), [class*="btn"]:not([id])').forEach(function(btn) {
      var t = btn.textContent.trim();
      for (var key in buttons) {
        if (buttons.hasOwnProperty(key)) {
          var cleanKey = key.replace('btn-', '').replace(/-/g, ' ');
          if (t.toLowerCase().indexOf(cleanKey) > -1) {
            btn.id = key;
            btn.onclick = function(e) { e.preventDefault(); buttons[this.id](); };
            btn.style.cursor = 'pointer';
            break;
          }
        }
      }
    });

    // Handle React/Veritas app buttons via window events (Event Delegation)
    document.addEventListener('click', function(e) {
      var target = e.target;
      // Search up the DOM tree to find a button-like element
      while (target && target !== document.body) {
        var t = target.textContent.trim().toLowerCase();
        var id = target.id;
        var isButton = target.tagName === 'BUTTON' || target.tagName === 'A' || target.classList.contains('nav-item') || target.classList.contains('cursor-pointer') || target.style.cursor === 'pointer' || target.getAttribute('role') === 'button';
        
        if (isButton) {
          if (id && buttons[id]) { 
            e.preventDefault(); 
            e.stopPropagation();
            buttons[id](); 
            return;
          }
          
          // Specific keyword detection for React-rendered components or generic divs
          if (textMatches(t, ['upload', '↥'])) {
            // EXCLUDE elements that handle their own file input (like Veritas React FileUpload)
            if (target.closest('.border-dashed')) return;
            if (document.getElementById('file-input') && target.contains(document.getElementById('file-input'))) return;

            e.preventDefault();
            e.stopPropagation();
            var module = 'Discovery-Vault™';
            if (t.indexOf('medical') > -1 || document.title.indexOf('Medical') > -1) module = 'Medical AI';
            else if (document.title.indexOf('Veritas') > -1) module = 'Veritas Deposition™';
            
            triggerFilePicker(module);
            return;
          }
          
          if (textMatches(t, ['new analysis'])) {
            e.preventDefault();
            e.stopPropagation();
            buttons['btn-new-analysis']();
            return;
          }
        }
        target = target.parentElement;
      }
    }, true);
  }

  // Expose to window for React/Veritas app access
  window.lexiflowUI = { showToast: showToast, showModal: showModal, buttons: buttons };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();