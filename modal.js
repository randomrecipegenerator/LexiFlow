/**
 * LexiFlow Consultation Modal
 * Handles the injection and logic for the Request Consultation modal.
 */

const ConsultationModal = {
    inject() {
        if (document.getElementById('consultationModal')) return;

        const modalHtml = `
            <div id="consultationModal" class="modal opacity-0 pointer-events-none fixed w-full h-full top-0 left-0 flex items-center justify-center z-[100] transition-opacity duration-250">
                <div class="modal-overlay absolute w-full h-full bg-slate-900 opacity-50" onclick="ConsultationModal.toggle()"></div>
                <div class="modal-container bg-white w-11/12 md:max-w-md mx-auto rounded-3xl shadow-2xl z-50 overflow-y-auto">
                    <div class="modal-content py-6 text-left px-8">
                        <div class="flex justify-between items-center pb-5 border-b border-slate-100">
                            <div>
                                <p class="text-2xl font-bold text-slate-900" id="modalTitle">Request Consultation</p>
                                <p class="text-sm text-slate-500 mt-1">Free 15-minute strategy session</p>
                            </div>
                            <div class="modal-close cursor-pointer p-2 hover:bg-slate-100 rounded-full transition" onclick="ConsultationModal.toggle()">
                                <i class="bi bi-x-lg"></i>
                            </div>
                        </div>
                        <form id="consultationForm" class="space-y-5 mt-6">
                            <div>
                                <label class="block text-sm font-semibold text-slate-700 mb-1">Full Name</label>
                                <input type="text" name="name" required placeholder="John Doe" 
                                    class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm p-3 border transition">
                            </div>
                            <div>
                                <label class="block text-sm font-semibold text-slate-700 mb-1">Work Email</label>
                                <input type="email" name="email" required placeholder="john@firm.com"
                                    class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm p-3 border transition">
                            </div>
                            <div>
                                <label class="block text-sm font-semibold text-slate-700 mb-1">Law Firm Name</label>
                                <input type="text" name="firm" required placeholder="Doe & Associates"
                                    class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm p-3 border transition">
                            </div>
                            <div>
                                <label class="block text-sm font-semibold text-slate-700 mb-1">Practice Area</label>
                                <select name="practice" class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm p-3 border transition bg-white">
                                    <option>Personal Injury</option>
                                    <option>Family Law</option>
                                    <option>Immigration</option>
                                    <option>Criminal Defense</option>
                                    <option>Mass Tort</option>
                                    <option>Other</option>
                                </select>
                            </div>
                            <div class="pt-2">
                                <button type="submit" id="submitBtn" class="w-full bg-blue-600 text-white font-bold py-4 rounded-xl hover:bg-blue-700 transition shadow-lg shadow-blue-200 flex items-center justify-center gap-2">
                                    <span>Send Request</span>
                                    <i class="bi bi-arrow-right"></i>
                                </button>
                            </div>
                            <p class="text-center text-xs text-slate-400">By submitting, you agree to our privacy policy.</p>
                        </form>
                    </div>
                </div>
            </div>
            <style>
                body.modal-active { overflow: hidden; }
            </style>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        document.getElementById('consultationForm').addEventListener('submit', ConsultationModal.handleSubmit);
    },

    toggle(title = 'Request Consultation') {
        const modal = document.getElementById('consultationModal');
        if (!modal) {
            this.inject();
            return this.toggle(title);
        }

        if (title) {
            document.getElementById('modalTitle').innerText = title;
        }

        const isHidden = modal.classList.contains('opacity-0');
        
        if (isHidden) {
            modal.classList.remove('opacity-0', 'pointer-events-none');
            document.body.classList.add('modal-active');
        } else {
            modal.classList.add('opacity-0', 'pointer-events-none');
            document.body.classList.remove('modal-active');
        }
    },

    async handleSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = document.getElementById('submitBtn');
        const originalBtnText = submitBtn.innerHTML;

        // Loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-arrow-repeat animate-spin"></i> <span>Sending...</span>';

        const formData = new FormData(form);
        
        try {
            // Use apiFetch if available, fallback to fetch
            const fetchFn = typeof apiFetch === 'function' ? apiFetch : async (url, opts) => {
                const apiUrl = url.startsWith('/api') ? url : `/api${url}`;
                return fetch(apiUrl, opts);
            };
            
            const response = await fetchFn('/demo-request', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Server error');
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Success state
                submitBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                submitBtn.classList.add('bg-green-600');
                submitBtn.innerHTML = '<i class="bi bi-check-lg"></i> <span>Success!</span>';
                
                setTimeout(() => {
                    alert('Thank you! Your consultation request has been received. Our team will be in touch shortly.');
                    ConsultationModal.toggle();
                    form.reset();
                    
                    // Reset button
                    submitBtn.disabled = false;
                    submitBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
                    submitBtn.classList.remove('bg-green-600');
                    submitBtn.innerHTML = originalBtnText;
                }, 500);
            } else {
                throw new Error(result.message || 'Unknown error');
            }
        } catch (error) {
            console.error('Consultation Request Error:', error);
            alert('Something went wrong. Please try again or email leads@lexiflow.co directly.');
            
            // Reset button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    }
};

// Auto-inject on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ConsultationModal.inject());
} else {
    ConsultationModal.inject();
}

// Global helper for onclick
window.toggleConsultation = (title) => ConsultationModal.toggle(title);
