/**
 * LexiFlow Professional UI Suite — Button Interaction Handler
 * Provides toast notifications and modal triggers for all action buttons.
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
    var toast = document.createElement('div');
    var icons = { success: 'bi-check-circle-fill', info: 'bi-info-circle-fill', warning: 'bi-exclamation-triangle-fill', error: 'bi-x-circle-fill' };
    var colors = { success: '#16a34a', info: '#3b82f6', warning: '#f97316', error: '#ef4444' };
    toast.style.cssText = 'display:flex;align-items:center;gap:12px;padding:14px 18px;background:#1e293b;border:1px solid #334155;border-left:4px solid ' + (colors[type] || '#3b82f6') + ';border-radius:10px;box-shadow:0 8px 32px rgba(0,0,0,0.4);color:#f1f5f9;font-family:Inter,sans-serif;font-size:14px;animation:slideIn 0.3s ease;';
    toast.innerHTML = '<i class="bi ' + (icons[type] || 'bi-info-circle-fill') + '" style="color:' + (colors[type] || '#3b82f6') + ';font-size:1.2rem;"></i><span style="flex:1;">' + message + '</span><button onclick="this.parentElement.remove()" style="background:none;border:none;color:#64748b;cursor:pointer;font-size:1.1rem;">&times;</button>';
    container.appendChild(toast);
    setTimeout(function() { if (toast.parentElement) { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(function() { toast.remove(); }, 300); } }, 4000);
  }

  // Add keyframe animation
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

  // Button click handlers
  var buttons = {
    // Dashboard
    'btn-suite-settings': function() { showModal('Suite Settings', '<p>Configure your LexiFlow Enterprise Suite preferences including notification settings, display options, and default views.</p><div style="margin-top:12px;padding:12px;background:#0f172a;border-radius:8px;border:1px solid #334155;"><div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Notification Preferences</span><span style="color:#22c55e;">Enabled</span></div><div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Auto-Refresh Interval</span><span style="color:#94a3b8;">30 seconds</span></div><div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Default Dashboard View</span><span style="color:#94a3b8;">Full Suite</span></div></div>', 'Save Changes', function() { showToast('Suite settings updated successfully.', 'success'); }); },

    // Discovery-Vault
    'btn-upload-docs': function() { showToast('📤 Upload dialog opened. Select documents to upload to Discovery-Vault.', 'info'); },
    'btn-new-mdl': function() { showModal('New MDL Case', '<p>Create a new MDL (Multi-District Litigation) case by entering case details below.</p><div style="margin-top:12px;"><div style="margin-bottom:12px;"><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Case Name</label><input type="text" placeholder="e.g., Opioid MDL 2804" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div><div style="margin-bottom:12px;"><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Jurisdiction</label><input type="text" placeholder="e.g., N.D. Ohio" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div><div><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Lead Counsel</label><input type="text" placeholder="Attorney name" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div></div>', 'Create Case', function() { showToast('New MDL case created successfully.', 'success'); }); },
    'btn-plus-dv': function() { showToast('Add new item to Discovery-Vault.', 'info'); },
    'btn-upload': function() { showToast('📤 File upload dialog opened.', 'info'); },

    // Medical AI
    'btn-new-analysis': function() { showModal('New Medical Analysis', '<p>Start a new AI-powered medical record analysis. Upload records or select from existing matters.</p><div style="margin-top:12px;padding:12px;background:#0f172a;border-radius:8px;border:1px solid #334155;"><div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Records Ready</span><span style="color:#22c55e;">347 pages</span></div><div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>AI Model</span><span style="color:#c9a84c;">Veritas Reasoning v3.2</span></div><div style="display:flex;justify-content:space-between;padding:6px 0;font-size:0.85rem;"><span>Est. Processing</span><span style="color:#94a3b8;">~45 seconds</span></div></div>', 'Start Analysis', function() { showToast('Medical analysis initiated. Results in ~45 seconds.', 'success'); }); },
    'btn-upload-ai': function() { showToast('📤 Upload medical records for AI analysis.', 'info'); },
    'btn-new-chronology': function() { showModal('New Medical Chronology', '<p>Generate an AI-powered medical chronology from uploaded records.</p><div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:12px;"><div style="padding:12px;background:#0f172a;border-radius:8px;border:1px solid #334155;text-align:center;cursor:pointer;hover:border-gold;"><div style="font-size:1.5rem;margin-bottom:4px;">📋</div><div style="font-size:0.8rem;color:#94a3b8;">Standard</div></div><div style="padding:12px;background:#0f172a;border-radius:8px;border:1px solid #c9a84c;text-align:center;"><div style="font-size:1.5rem;margin-bottom:4px;">⚡</div><div style="font-size:0.8rem;color:#c9a84c;">Detailed + Findings</div></div></div>', 'Generate Chronology', function() { showToast('Medical chronology generated with 347 entries.', 'success'); }); },
    'btn-plus-ai': function() { showToast('Add new analysis item.', 'info'); },

    // Settlement Predictor
    'btn-run-valuation': function() { showModal('New Settlement Valuation', '<p>Run an AI-powered settlement valuation based on case data.</p><div style="margin-top:12px;"><div style="margin-bottom:12px;"><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Case Type</label><select style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"><option>Medical Malpractice</option><option>Personal Injury</option><option>Product Liability</option><option>Wrongful Death</option></select></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;"><div><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Severity Score</label><input type="number" value="8" min="1" max="10" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div><div><label style="display:block;font-size:0.8rem;color:#94a3b8;margin-bottom:4px;">Liability %</label><input type="number" value="75" min="0" max="100" style="width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f1f5f9;font-family:inherit;font-size:0.85rem;"></div></div></div>', 'Run Valuation', function() { showToast('Settlement prediction complete: $1,250,000 - $1,800,000 range (94% confidence).', 'success'); }); },

    // Compliance Shield
    'btn-download-soc2': function() { showToast('📄 SOC 2 Type II report download started.', 'success'); },
    'btn-security-settings': function() { showModal('Security Settings', '<p>Configure compliance and security settings for your firm.</p><div style="margin-top:12px;"><div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #334155;"><span style="font-size:0.85rem;">HIPAA Compliance Mode</span><span style="color:#22c55e;font-size:0.85rem;">Active</span></div><div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #334155;"><span style="font-size:0.85rem;">Data Retention (days)</span><span style="color:#94a3b8;font-size:0.85rem;">365</span></div><div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #334155;"><span style="font-size:0.85rem;">Audit Logging</span><span style="color:#22c55e;font-size:0.85rem;">Enabled</span></div><div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;"><span style="font-size:0.85rem;">MFA Required</span><span style="color:#22c55e;font-size:0.85rem;">Enabled</span></div></div>', 'Save Settings', function() { showToast('Security settings saved successfully.', 'success'); }); },
  };

  // Initialize: add IDs and click handlers
  function init() {
    // Dashboard
    var el = document.querySelector('#dashboard-settings-btn') || document.querySelector('button:has(.bi-gear)');
    document.querySelectorAll('button').forEach(function(btn) {
      var text = btn.textContent.trim().toLowerCase();
      var html = btn.innerHTML;

      // Suite Settings
      if (html.indexOf('bi-gear') > -1 && text.indexOf('settings') > -1) { btn.id = 'btn-suite-settings'; }
      // Upload Docs
      else if (html.indexOf('bi-upload') > -1 && text.indexOf('upload') > -1 && text.indexOf('docs') > -1) { btn.id = 'btn-upload-docs'; }
      // New MDL
      else if (text.indexOf('new mdl') > -1 || text.indexOf('new mdl case') > -1) { btn.id = 'btn-new-mdl'; }
      // Upload Button
      else if (html.indexOf('bi-upload') > -1 && text.indexOf('upload') > -1 && !btn.id) { btn.id = 'btn-upload'; }
      // New Analysis
      else if (text.indexOf('new analysis') > -1) { btn.id = 'btn-new-analysis'; }
      // Upload Batch
      else if (text.indexOf('upload batch') > -1) { btn.id = 'btn-upload-batch'; }
      // New Chronology
      else if (text.indexOf('new chronology') > -1) { btn.id = 'btn-new-chronology'; }
      // Run Valuation
      else if (text.indexOf('run new valuation') > -1 || text.indexOf('run valuation') > -1) { btn.id = 'btn-run-valuation'; }
      // Download SOC 2
      else if (text.indexOf('download soc 2') > -1) { btn.id = 'btn-download-soc2'; }
      // Security Settings
      else if (text.indexOf('security settings') > -1) { btn.id = 'btn-security-settings'; }
      // Plus icon buttons
      else if (html.indexOf('bi-plus') > -1 || html.indexOf('⊕') > -1) {
        btn.id = btn.closest('[class*="discov"]') ? 'btn-plus-dv' : 'btn-plus-ai';
      }
      // Upload icon buttons (↥)
      else if (html.indexOf('↥') > -1 || html.indexOf('bi-file-earmark-arrow-up') > -1) {
        btn.id = btn.closest('[class*="medic"]') ? 'btn-upload-ai' : 'btn-upload';
      }

      // Wire up click handler
      if (btn.id && buttons[btn.id]) {
        btn.onclick = function(e) {
          e.preventDefault();
          buttons[this.id]();
        };
      }
    });

    // Manual fallback for buttons without IDs
    document.querySelectorAll('button.v-btn:not([id])').forEach(function(btn) {
      var text = btn.textContent.trim();
      if (text.indexOf('Suite Settings') > -1) { btn.id = 'btn-suite-settings'; btn.onclick = function(e) { e.preventDefault(); buttons['btn-suite-settings'](); }; }
      else if (text.indexOf('Upload Docs') > -1) { btn.id = 'btn-upload-docs'; btn.onclick = function(e) { e.preventDefault(); buttons['btn-upload-docs'](); }; }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();