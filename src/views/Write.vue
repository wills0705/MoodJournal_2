<template>
  <div class="journal-write">
    <div class="journal-write-header">
      <div class="header-date">
        {{ currentDate }}
      </div>
    </div>
    <div class="journal-write-content">
      <a-textarea v-model:value="journalContent" placeholder="Click here to start write your new journal" />
    </div>
    <div class="journal-write-save">
      <a-button type="primary" size="large" :loading="isLoading" @click="saveText">Save</a-button>

    </div>
  </div>
</template>
<script>
import { formatDate } from '../lib/util';
const SAVE_DEALY = 1000;
export default {
  name: 'write',
  props: {
    journalList: {
      type: Array,
      default: []
    }
  },
  data() {
    return {
      // journal content
      journalContent: '',
      // date
      currentDate: formatDate(new Date()),
      // saving or not
      isLoading: false,
    }
  },
  methods: {
    // clear
    clearText() {
      this.journalContent = ''
    },
    // save journal
    saveText() {
      if (!this.journalContent) {
        return;
      }
      this.isLoading = true;
      setTimeout(() => {
        this.isLoading = false;
        const d = new Date();
        const textObj = {
          currentDate: formatDate(d),
          currentTime: d,
          content: this.journalContent,
          isApproved: false // 新增审批状态字段
        }
        this.$emit('updateJournal', textObj)
        this.showTopic(this.journalContent)
        this.clearText();
      }, SAVE_DEALY)
    },
    // show topic
    showTopic(text){
      const data = text;
    },
  },
};
</script>
<style lang="less" scoped>
.journal-write {
  height: 100%;

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

  &-save {
    margin-top: 20px;

    flex: none;


    .ant-btn {
      width: 100%;
      height: 50px;
    }

  }
}
</style>