<template>
  <div class="pg-root">
    <div class="pg-card">
      <div class="pg-header">
        <div class="pg-title">Before you start</div>
        <div class="pg-sub">Please review {{ docs.length }} short documents</div>
        <div class="pg-progress">
          <div class="pg-progress-bar" :style="{ width: ((step+1)/docs.length*100)+'%' }"></div>
        </div>
      </div>

      <div class="pg-body">
        <div class="pg-doc-title">{{ docs[step].title }}</div>

        <iframe
          class="pg-frame"
          :src="docs[step].url"
          frameborder="0"
          @load="frameLoaded=true"
        ></iframe>

        <label class="pg-checkbox">
          <input type="checkbox" v-model="confirmedStep" />
          I have read this page and agree
        </label>

        <!-- Only show extra consent checkboxes on final page -->
        <div v-if="step === docs.length - 1">
          <label class="pg-checkbox">
            <input type="checkbox" v-model="extraConfirmA" />
            YES, I agree to participate in this study.
          </label>

          <label class="pg-checkbox">
            <input type="checkbox" v-model="extraConfirmB" />
            I agree to allow my study data to be stored and used for this research as described in the Informed Consent
          </label>

          <label class="pg-checkbox">
            <input type="checkbox" v-model="extraConfirmC" />
            I agree to allow the researchers to personally send me the results of the study via email
          </label>

          <label class="pg-checkbox">
            <input type="checkbox" v-model="extraConfirmD" />
            I do not wish to receive the study results via email
          </label>
        </div>
      </div>

      <div class="pg-actions">
        <button class="pg-btn" :disabled="step===0" @click="prev">Back</button>

        <button
          v-if="step < docs.length-1"
          class="pg-btn primary"
          :disabled="!confirmedStep"
          @click="next"
        >
          Next
        </button>

        <button
          v-else
          class="pg-btn success"
          :disabled="!canAgreeAndContinue"
          @click="$emit('accepted')"
        >
          I agree & continue
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PolicyGate',
  props: {
    docs: {
      type: Array,
      required: true, // [{title, url}]
    },
  },
  data() {
    return {
      step: 0,
      confirmedStep: false,
      frameLoaded: false,
      extraConfirmA: false,
      extraConfirmB: false,
      extraConfirmC: false,
      extraConfirmD: false,
    };
  },
  computed: {
    canAgreeAndContinue() {
      if (this.step !== this.docs.length - 1) return this.confirmedStep;

      const requiredChecked =
        this.confirmedStep && this.extraConfirmA && this.extraConfirmB;

      const emailChoiceChecked =
        (this.extraConfirmC && !this.extraConfirmD) ||
        (!this.extraConfirmC && this.extraConfirmD);

      return requiredChecked && emailChoiceChecked;
    },
  },
  watch: {
    extraConfirmC(val) {
      if (val) this.extraConfirmD = false;
    },
    extraConfirmD(val) {
      if (val) this.extraConfirmC = false;
    },
  },
  methods: {
    next() {
      if (this.step < this.docs.length - 1) {
        this.step++;
        this.confirmedStep = false;
        this.frameLoaded = false;
        this.extraConfirmA = false;
        this.extraConfirmB = false;
        this.extraConfirmC = false;
        this.extraConfirmD = false;
      }
    },
    prev() {
      if (this.step > 0) {
        this.step--;
        this.confirmedStep = true;
        this.extraConfirmA = false;
        this.extraConfirmB = false;
        this.extraConfirmC = false;
        this.extraConfirmD = false;
      }
    },
  },
};
</script>

<style scoped>
.pg-root{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:#00000066;z-index:9999}
.pg-card{width:min(920px,92vw);height:720px;background:#fff;border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,.25);display:flex;flex-direction:column}
.pg-header{padding:16px 20px 0}
.pg-title{font-size:20px;font-weight:800}
.pg-sub{margin-top:4px;color:#555}
.pg-progress{height:6px;background:#edf2f7;border-radius:999px;margin:12px 0 8px}
.pg-progress-bar{height:100%;background:#2d7dfe;border-radius:999px;transition:width .25s}
.pg-body{flex:1;padding:12px 20px;display:flex;flex-direction:column;gap:10px}
.pg-doc-title{font-weight:700}
.pg-frame{flex:1;width:100%;border:1px solid #eee;border-radius:10px;background:#fafafa}

.pg-checkbox{
  margin-top:8px;
  user-select:none;
  display:flex;
  align-items:flex-start;
  gap:8px;
}

.pg-actions{display:flex;gap:8px;justify-content:flex-end;padding:12px 20px 16px;border-top:1px solid #f0f0f0}
.pg-btn{padding:8px 14px;border-radius:8px;border:1px solid #d0d7de;background:#fff;cursor:pointer}
.pg-btn:disabled{opacity:.5;cursor:not-allowed}
.primary{background:#2d7dfe;border-color:#2d7dfe;color:#fff}
.success{background:#16a34a;border-color:#16a34a;color:#fff}
</style>
