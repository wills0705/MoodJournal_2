<template>
  <div class="journal-write">
    <!-- Date line -->
    <div class="journal-write-date">
      {{ displayDate }}
    </div>

    <!-- Textarea card -->
    <div class="journal-write-card">
      <a-textarea
        v-model:value="journalContent"
        placeholder="Click here to start write your new journal"
      />
    </div>

    <!-- Footer: instruction + styles + save -->
    <div class="journal-write-footer">
      <div class="footer-instruction">
        Please select the style of image you wish to generate based on your journal entry.
      </div>

      <div class="footer-row">
        <div class="footer-left">
          <!-- Order aligned with your mockup (feel free to reorder) -->
          <a-button @click="showModal(1)" :type="activeButton === 1 ? 'primary' : 'default'">Line art</a-button>
          <a-button @click="showModal(2)" :type="activeButton === 2 ? 'primary' : 'default'">Comic book</a-button>
          <a-button @click="showModal(3)" :type="activeButton === 3 ? 'primary' : 'default'">Pixel art</a-button>
          <a-button @click="showModal(4)" :type="activeButton === 4 ? 'primary' : 'default'">Analog film</a-button>
          <a-button @click="showModal(5)" :type="activeButton === 5 ? 'primary' : 'default'">Neon punk</a-button>
          <a-button @click="showModal(6)" :type="activeButton === 6 ? 'primary' : 'default'">Digital art</a-button>
        </div>

        <div class="footer-right">
          <a-button
            class="save-btn"
            size="large"
            :loading="isLoading"
            :disabled="!canSave"
            aria-disabled="!canSave"
            @click="saveText"
          >
            Save
          </a-button>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <a-modal
      v-for="i in 6"
      :key="i"
      :open="modalVisible[i]"
      :title="`Style ${i}`"
      :closable="false"
      wrapClassName="mj-style-modal"
      @ok="handleModalOk(i)"
      @cancel="handleModalCancel(i)"
    >
      <template v-if="i === 1">
        <p>Line Art Preview</p>
        <img src="/lineart.png" alt="Line Art" class="modal-preview" />
      </template>
      <template v-else-if="i === 2">
        <p>Comic Book Preview</p>
        <img src="/comicbook.png" alt="Comic Book" class="modal-preview" />
      </template>
      <template v-else-if="i === 3">
        <p>Pixel Art Preview</p>
        <img src="/pixalart.png" alt="Pixel Art" class="modal-preview" />
      </template>
      <template v-else-if="i === 4">
        <p>Analog Film Preview</p>
        <img src="/analogfilm.jpg" alt="Analog Film" class="modal-preview" />
      </template>
      <template v-else-if="i === 5">
        <p>Neon Punk Preview</p>
        <img src="/neonpunk.png" alt="Neon Punk" class="modal-preview" />
      </template>
      <template v-else-if="i === 6">
        <p>Digital Art Preview</p>
        <img src="/digitalart.jpg" alt="Digital Art" class="modal-preview" />
      </template>
    </a-modal>
  </div>
</template>

<script>
import { formatDate, monthMap, dayMap } from '../lib/util';
import { getDatabase, ref, set } from 'firebase/database';

const SAVE_DELAY = 1000;

export default {
  name: 'write',
  props: {
    journalList: { type: Array, default: [] },
    saveStatus: { type: String, default: 'idle' }
  },
  data() {
    return {
      journalContent: '',
      currentDate: formatDate(new Date()),
      isLoading: false,
      modalVisible: { 1: false, 2: false, 3: false, 4: false, 5: false, 6: false },
      activeButton: null
    }
  },
  computed: {
    canSave() {
      return !!this.activeButton && !!this.journalContent.trim();
    },
    displayDate() {
      const d = new Date();
      const monthFull = monthMap[d.getMonth()] || '';
      const monthAbbrev = monthFull ? monthFull.slice(0, 3) + '.' : '';
      const day = String(d.getDate()).padStart(2, '0');
      const year = d.getFullYear();
      const weekday = dayMap[d.getDay()] || '';
      return `${monthAbbrev}${day}.${year} (${weekday})`;
    }
  },
  watch: {
    saveStatus(newVal) {
      if (newVal === 'success' || newVal === 'error' || newVal === 'idle') {
        this.isLoading = false;
      }
    }
  },
  methods: {
    clearText() { this.journalContent = '' },
    saveText() {
      // Hard guard: require content and style selection
      if (!this.journalContent.trim()) {
        this.$message?.warning?.('Please write something first.');
        return;
      }
      if (!this.activeButton) {
        this.$message?.warning?.('Please choose an image style.');
        return;
      }

      this.isLoading = true;
      setTimeout(() => {
        const d = new Date();
        const textObj = {
          currentDate: formatDate(d),
          currentTime: d,
          content: this.journalContent.trim(),
          isApproved: false,
          buttonNumber: this.activeButton
        };
        this.$emit('updateJournal', textObj);
        this.clearText();
      }, SAVE_DELAY);
    },
    showModal(buttonNumber) {
      this.modalVisible[buttonNumber] = true;
      this.activeButton = buttonNumber;
    },
    async handleModalCancel(i) {
      this.modalVisible[i] = false;
      if (this.activeButton === i) this.activeButton = null;
    },
    async handleModalOk(buttonNumber) {
      this.modalVisible[buttonNumber] = false;
      this.activeButton = buttonNumber;
      try {
        const db = getDatabase();
        const buttonRef = ref(db, 'buttonSelections/' + new Date().getTime());
        await set(buttonRef, { buttonNumber, timestamp: new Date().toISOString() });
      } catch (error) {
        console.error('Error saving button selection:', error);
      }
    }
  },
};
</script>

<style lang="less" scoped>
::v-deep(.ant-modal-body) { max-height: 70vh; overflow: auto; }
::v-deep(.ant-modal) { width: auto !important; max-width: 90vw; top: 24px; }
::v-deep(.ant-modal-content) { max-width: 90vw; }

.modal-preview {
  max-width: 100%;
  max-height: 60vh;
  height: auto;
  object-fit: contain;
  display: block;
  margin: 0 auto;
  border-radius: 8px;
}

.journal-write {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.journal-write-date {
  font-size: 20px;
  font-weight: 700;
  padding: 2px 2px;
}

.journal-write-card {
  flex: 1 1 auto;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
  overflow: hidden;
  padding: 10px;

  textarea {
    border: none;
    box-shadow: none;
    resize: none;
    height: 100%;
    min-height: 420px;
    padding: 14px;
    font-size: 14px;
    line-height: 1.5;
  }

  ::v-deep(.ant-input:focus),
  ::v-deep(.ant-input-focused) {
    box-shadow: none;
  }
}

.journal-write-footer {
  flex: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-instruction {
  color: #4b5563;
  font-size: 14px;
}

.footer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.footer-left {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;

  ::v-deep(.ant-btn) {
    border-radius: 12px;
    height: 40px;
    padding: 0 18px;
    border-color: #d1d5db;
    color: #111827;
    background: #ffffff;
  }

  ::v-deep(.ant-btn:hover),
  ::v-deep(.ant-btn:focus),
  ::v-deep(.ant-btn:active) {
    border-color: #111827 !important;
    color: #111827 !important;
    background: #ffffff !important;
  }

  ::v-deep(.ant-btn-primary) {
    background: #111827 !important;
    border-color: #111827 !important;
    color: #ffffff !important;
  }

  ::v-deep(.ant-btn-primary:hover),
  ::v-deep(.ant-btn-primary:focus),
  ::v-deep(.ant-btn-primary:active) {
    background: #000000 !important;
    border-color: #000000 !important;
    color: #ffffff !important;
  }
}

/* ✅ MOVE THESE OUTSIDE footer-left */
::v-deep(.ant-modal-footer .ant-btn) {
  border-radius: 10px;
  border-color: #d1d5db !important;
  color: #111827 !important;
  background: #ffffff !important;
}

::v-deep(.ant-modal-footer .ant-btn:hover),
::v-deep(.ant-modal-footer .ant-btn:focus),
::v-deep(.ant-modal-footer .ant-btn:active) {
  border-color: #111827 !important;
  color: #111827 !important;
  background: #ffffff !important;
}

::v-deep(.ant-modal-footer .ant-btn-primary) {
  background: #111827 !important;
  border-color: #111827 !important;
  color: #ffffff !important;
}

::v-deep(.ant-modal-footer .ant-btn-primary:hover),
::v-deep(.ant-modal-footer .ant-btn-primary:focus),
::v-deep(.ant-modal-footer .ant-btn-primary:active) {
  background: #000000 !important;
  border-color: #000000 !important;
  color: #ffffff !important;
}

/* Optional: kill the blue focus ring */
::v-deep(.ant-btn:focus-visible) {
  outline: none !important;
  box-shadow: none !important;
}

.footer-right {
  flex: none;
}

.save-btn {
  width: 140px;
  height: 50px;
  border-radius: 14px;
  border: none;
  background: #111827;
  color: #fff;
  font-weight: 700;
}

.save-btn:hover {
  background: #0b1220;
  color: #fff;
}

.save-btn[disabled] {
  background: #e5e7eb !important;
  color: #9ca3af !important;
}
</style>
