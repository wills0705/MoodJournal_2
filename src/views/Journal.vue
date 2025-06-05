<template>
  <div class="journal-list">
    <div class="journal-list-list">
      <div
        :class="['list-item', currentJournal.timestamp === item.timestamp ? 'active-item' : '']"
        v-for="(item, index) in list"
        :key="index"
        @click="showJournalDetail(item)"
      >
        <div class="list-item-title">
          {{ item.title }}
        </div>
        <div class="list-item-date">
          {{ item.enDate }}
        </div>
      </div>
    </div>

    <div class="journal-list-content" v-if="currentJournal.content">
      <!-- Left Panel: Journal Info -->
      <div class="journal-list-content-left">
        <div class="content-title">
          <div class="content-title-text">
            <div class="month">{{ currentJournal.enDate.slice(0, -5) }}</div>
            <div class="week">{{ currentJournal.enDate.slice(-4) }}, {{ currentJournal.weekDay }}</div>
          </div>
          <div class="content-title-icon">
            <img :src="currentFace" alt="" class="mood-icon" />
          </div>
        </div>

        <div class="content-container">
          <div class="content-container-title">
            {{ currentJournal.title }}
          </div>
          <div class="content-container-content">
            {{ currentJournal.content }}
          </div>
        </div>

        <div class="content-rate">
          <div class="content-rate-tip">
            Rate your mood today
          </div>
          <div class="content-rate-icon">
            <img
              v-for="(item, index) in faceList"
              :key="index"
              :src="faceIconUrl(item)"
              class="mood-icon"
              @click="setFace(item, index)"
            />
          </div>
        </div>


      </div>

      <!-- Right Panel: AI Image (base64) or fallback cat -->
      <div class="journal-list-content-right">
        <div class="content-img">
          <template v-if="currentJournal.isApproved">
            <img
              :src="currentJournal.sdImage"
              alt="Generated Image"
              class="ai-img"
              @error="handleImageError"
            />
          </template>
          <div v-else class="pending-message">
            The picture is successfully generated, please wait patiently for review.
          </div>
          <div class="img-text">
            AI-Generated Image
          </div>
        </div>

        
      </div>
    </div>
  </div>
</template>

<script>
import { doc, updateDoc } from 'firebase/firestore';
import { db } from '../firebase';
import { dayMap, monthMap } from '../lib/util';

export default {
  name: 'journal',
  props: {
    journalList: {
      type: Array,
      default: []
    }
  },
  data() {
    return {
      list: [],
      currentJournal: {
        id: '',
        title: '',
        content: '',
        currentDate: '',
        timestamp: '',
        mood: 2,
        sdImage: '' // base64 image (data URI) from Firestore
      },
      faceList: [
        '../assets/image/mood-sad.png',
        '../assets/image/mood-frown.png',
        '../assets/image/mood-normal.png',
        '../assets/image/mood-smile.png',
        '../assets/image/mood-laugh.png'
      ],
      currentFace: '',
      fallbackCat: '' // We'll compute in mounted()
    };
  },
  watch: {
    journalList() {
      this.filterJournal();
    }
  },
  activated() {
    this.filterJournal();
  },
  methods: {
    handleImageError(e) {
    e.target.src = this.fallbackCat; // 显示备用图片
    },
    faceIconUrl(path) {
      // Convert relative path to full URL
      return new URL(path, import.meta.url).href;
    },
    setFace(item, index) {
      // Update local mood & face
      this.currentFace = this.faceIconUrl(item);
      this.currentJournal.mood = index;

      // Persist mood to Firestore
      this.updateJournalMood();
    },
    showJournalDetail(journal) {
      this.currentJournal = {
        ...journal
      };

      // Update face icon based on mood
      if (journal.mood >= 0 && journal.mood < this.faceList.length) {
        this.currentFace = this.faceIconUrl(this.faceList[journal.mood]);
      } else {
        this.currentFace = this.faceIconUrl('../assets/image/mood-normal.png');
      }
    },
    filterJournal() {
      this.list = this.journalList.map(item => {
        return {
          ...item,
          enDate: this.formatEnDate(item.currentDate),
          weekDay: this.getWeekDay(item.currentDate)
        };
      });
    },
    getWeekDay(date) {
      const d = new Date(date);
      return dayMap[d.getDay()];
    },
    formatEnDate(date) {
      const d = new Date(date);
      const m = monthMap[d.getMonth()].slice(0, 3);
      const dd = d.getDate();
      const y = d.getFullYear();
      return `${m}.${dd}.${y}`;
    },
    async updateJournalMood() {
      if (!this.currentJournal.id) return;
      try {
        const docRef = doc(db, 'journalList', this.currentJournal.id);
        await updateDoc(docRef, { mood: this.currentJournal.mood });
        this.$message && this.$message.success('Mood updated successfully!');
      } catch (err) {
        console.error('Error updating mood in Firestore:', err);
      }
    }
  },
  mounted() {
    this.filterJournal();
    // Precompute fallback cat image (relative or public path)
    this.fallbackCat = new URL('../assets/image/cat.jpeg', import.meta.url).href;
    this.currentFace = this.faceIconUrl('../assets/image/mood-normal.png');
  }
};
</script>

<style lang="less" scoped>
.pending-message {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-style: italic;
  padding: 20px;
  border: 2px dashed #eee;
  border-radius: 8px;
  margin: 20px 0;
}
.journal-list {
  height: 100%;
  overflow: hidden;
  display: flex;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  box-sizing: border-box;

  &-list {
    height: 100%;
    overflow: auto;
    width: 20%;
    background: rgb(244, 248, 255);

    .active-item {
      background: rgb(230, 235, 248);
    }

    .list-item {
      padding: 10px 16px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      font-weight: bold;
      cursor: pointer;

      &-title {
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        overflow: hidden;
        text-overflow: ellipsis;
        word-break: break-all;
      }

      &-date {
        margin-top: 10px;
      }

      &:last-of-type {
        border-bottom: none;
      }

      &:hover {
        background: rgb(230, 235, 248);
      }
    }
  }

  &-content {
    height: 100%;
    width: 80%;
    flex: auto;
    display: flex;

    &-left {
      width: 50%;
      height: 100%;
      overflow: auto;
      padding: 20px;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;

      .content-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        padding: 10px;

        &-text {
          .month {
            font-size: 24px;
            font-weight: bold;
          }

          .week {
            margin-top: 4px;
          }
        }

        &-icon {
          .mood-icon {
            width: 30px;
            height: 30px;
          }
        }
      }

      .content-container {
        padding: 20px;
        flex: auto;
        overflow: auto;

        &-title {
          font-size: 24px;
          font-weight: bold;
        }

        &-content {
          line-height: 20px;
          margin-top: 24px;
        }
      }

      .content-rate {
        padding: 20px 20px 0 20px;

        &-tip {
          font-size: 16px;
          font-weight: bold;
        }

        &-icon {
          display: flex;
          align-items: center;
          justify-content: center;

          .mood-icon {
            width: 40px;
            height: 40px;
            margin-left: 8px;
            margin-top: 10px;
            cursor: pointer;
          }
        }
      }

      .content-text {
        padding: 20px;
        font-size: 16px;
        font-weight: bold;
      }
    }

    &-right {
      width: 50%;
      height: 100%;
      overflow: auto;
      padding: 20px;
      box-sizing: border-box;
      border-left: 1px solid rgba(0, 0, 0, 0.1);
      display: flex;
      flex-direction: column;

      .content-img {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        flex: auto;
        width: 100%;

        .ai-img {
          width: 100%;
          height: auto;
        }

        .img-text {
          margin-top: 20px;
        }
      }

      .content-tip {
        flex: none;
        color: rgba(198, 108, 116);
      }
    }
  }
}
</style>
