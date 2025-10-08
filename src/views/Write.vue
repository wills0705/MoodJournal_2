<template>
  <div class="journal-write">
    <div class="journal-write-header">
      <div class="header-date">{{ currentDate }}</div>
    </div>
    <div class="journal-write-content">
      <a-textarea v-model:value="journalContent" placeholder="Click here to start write your new journal" />
    </div>
    <div class="journal-write-footer">
      <div class="footer-left">
        <a-button @click="showModal(1)" :type="activeButton === 1 ? 'primary' : 'default'">Line art</a-button>
        <a-button @click="showModal(2)" :type="activeButton === 2 ? 'primary' : 'default'">Comic book</a-button>
        <a-button @click="showModal(3)" :type="activeButton === 3 ? 'primary' : 'default'">Pixel art</a-button>
        <a-button @click="showModal(4)" :type="activeButton === 4 ? 'primary' : 'default'">Analog film</a-button>
        <a-button @click="showModal(5)" :type="activeButton === 5 ? 'primary' : 'default'">Neon punk</a-button>
      </div>
      <div class="footer-right">
        <a-button type="primary" size="large" :loading="isLoading" @click="saveText">Save</a-button>
      </div>
    </div>
    <a-modal
      v-for="i in 5"
      :key="i"
      :open="modalVisible[i]"
      :title="`Style ${i}`"
      :closable="false"
      @ok="handleModalOk(i)"
    >
      <template v-if="i === 1">
        <p>Line Art Preview</p>
        <img src="/lineart.png" alt="Line Art" class="modal-preview"/>
      </template>
      <template v-else-if="i === 2">
        <p>Comic Book Preview</p>
        <img src="/comicbook.png" alt="Comic Book" class="modal-preview"/>
      </template>
      <template v-else-if="i === 3">
        <p>Pixel Art Preview</p>
        <img src="/pixalart.png" alt="Pixel Art" class="modal-preview"/>
      </template>
      <template v-else-if="i === 4">
        <p>Analog Film Preview</p>
        <img src="/analogfilm.png" alt="Analog Film" class="modal-preview"/>
      </template>
      <template v-else-if="i === 5">
        <p>Neon Punk Preview</p>
        <img src="/neonpunk.png" alt="Neon Punk" class="modal-preview"/>
      </template>
    </a-modal>
  </div>
</template>

<script>
import { formatDate } from '../lib/util';
import { getDatabase, ref, set } from 'firebase/database';

const SAVE_DELAY = 1000;

export default {
  name: 'write',
  props: { journalList: { type: Array, default: [] } },
  data() {
    return {
      journalContent: '',
      currentDate: formatDate(new Date()),
      isLoading: false,
      modalVisible: { 1: false, 2: false, 3: false, 4: false, 5: false },
      activeButton: null
    }
  },
  methods: {
    clearText() { this.journalContent = '' },
    stopLoading() {
    this.isLoading = false;
    },
    saveText() {
      if (!this.journalContent) return;
      this.isLoading = true;
      setTimeout(() => {
        const d = new Date();
        const textObj = {
          currentDate: formatDate(d),
          currentTime: d,
          content: this.journalContent,
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
    async handleModalOk(buttonNumber) {
      this.modalVisible[buttonNumber] = false;
      this.activeButton = buttonNumber;
      try {
        const db = getDatabase();
        const buttonRef = ref(db, 'buttonSelections/' + new Date().getTime());
        await set(buttonRef, {
          buttonNumber: buttonNumber,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('Error saving button selection:', error);
      }
    }
  },
};
</script>

::v-deep(.ant-modal-body) {
  max-height: 70vh;
  overflow: auto;
}

::v-deep(.ant-modal) {
  width: auto !important;
  max-width: 90vw;
  top: 24px;
}

::v-deep(.ant-modal-content) {
  max-width: 90vw;
}

.modal-preview {
  max-width: 100%;
  max-height: 60vh;
  height: auto;
  object-fit: contain;
  display: block;
  margin: 0 auto;
  border-radius: 8px;
}

<style lang="less" scoped>
.journal-write {
  height: 100%;
  display: flex;
  flex-direction: column;

  &-header {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex: none;

    .header-date {
      background: #DFFAF1;
      padding: 6px 30px;
      border-radius: 14px;
    }
  }

  &-content {
    margin-top: 20px;
    flex: auto;
    border-radius: 8px;
    background: #fff;
    overflow: hidden;
    height: 80%;

    textarea {
      border-radius: 10px;
      height: 100%;
    }
  }

  &-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    flex: none;

    .footer-left {
      display: flex;
      gap: 8px;
    }

    .footer-right {
      .ant-btn {
        width: 100%;
        height: 50px;
      }
    }
  }
}
</style>