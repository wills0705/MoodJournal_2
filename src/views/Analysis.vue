<template>
  <div class="analysis-journal">
    <div class="insight-tab">
      <div class="insight-tab-item">Mood trend view</div>
      <!-- <div class="insight-tab-item">Topic trend view</div> -->
    </div>
    <div class="insight-content">
      <div class="insight-content-header">
        <div class="header-date">
          {{ currentMonth }} {{ currentYear }}
        </div>
        <div class="header-select"></div>
      </div>
      <div class="insight-content-date">
        <div class="date-left">
          <div class="date-left-change-week">
            <div class="date-left-change-week-item" @click="handleWeekChange(-1)">
              <LeftCircleOutlined :style="{ color: '#2d7dfe', fontSize: '26px' }" />
            </div>
            <div :class="['date-left-change-week-item', weekIndex === 0 ? 'disable-change' : '']"
              @click="handleWeekChange(1)">
              <RightCircleOutlined :style="{ color: '#2d7dfe', fontSize: '26px' }" />
            </div>
          </div>
          <div class="date-left-mood-item" v-for="(item, index) in moodList" :key="index">
            {{ item }}
          </div>
        </div>
        <div class="date-right" v-if="lineVisible">
          <div :class="['date-right-item', item.fullDate === currentDate ? 'active-date' : '']"
            v-for="(item, index) in weekList" :key="index">
            <div class="date-title">
              <div class="day">{{ item.day }}</div>
              <div class="date">{{ item.date }}</div>
            </div>
            <div class="mood-item" v-for="(_text, ind) in moodList" :key="ind">
              <div
                :class="['mood-item-img', dateMoodList[index] && dateMoodList[index].currentDate === currentFormatDate ? 'active-img' : '']"
                v-if="dateMoodList[index] && dateMoodList[index].mood === moodList.length - ind  - 1 && dateMoodList[index].currentDate === item.fullDate"
                :ref="dateMoodList[index] && dateMoodList[index].mood === moodList.length - ind  - 1 && dateMoodList[index].currentDate === item.fullDate ? `anchor${index}` : ''"
                @click="showContent(dateMoodList[index])">
                <img :src="dateMoodList[index].sdImage" alt="wait approve" class="mood-img">
              </div>
            </div>
          </div>
          <div class="line line1"></div>
          <div class="line line2"></div>
          <div class="line line3"></div>
          <div class="line line4"></div>
          <div class="line line5"></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { notification } from 'ant-design-vue';
import { LeftCircleOutlined, RightCircleOutlined } from '@ant-design/icons-vue';
import LeaderLine from 'leader-line-vue'
import { getDateInfo, monthMap, getWeekDates, formatDate } from '../lib/util'

const dateInfo = getDateInfo(new Date());
export default {
  name: 'analysis',
  components: { LeftCircleOutlined, RightCircleOutlined },
  props: {
    journalList: {
      type: Array,
      default: []
    }
  },
  created() {
    this.handleMoodList();
  },
  data() {
    return {
      currentMonth: monthMap[dateInfo.month - 1],
      currentYear: dateInfo.year,
      currentDate: dateInfo.fullDate,
      currentFormatDate: formatDate(new Date()),
      weekList: getWeekDates(0),
      dateMoodList: [],
      moodList: ['Great','Good','Neutral','Mooday','Down'],
      modalVisible: false,
      currentContent: '',
      weekIndex: 0,
      lineVisible: true,
      lineArr: [],
    }
  },
  watch: {
    // LIVE update when journals change
    journalList: {
      handler() {
        this.handleMoodList();
        // redraw connection lines after DOM updates
        this.$nextTick(() => {
          this.destroyLine();
          setTimeout(() => this.handleLine(), 10);
        });
      },
      deep: true
    }
  },
  methods: {
    handleWeekChange(flag) {
      if (flag > 0) {
        if (this.weekIndex === 0) return;
        this.weekIndex++
      } else {
        this.weekIndex--
      }
      this.destroyLine();
      this.lineVisible = false;
      this.$nextTick(() => {
        this.weekList = getWeekDates(this.weekIndex);
        this.setCurrentMonthAndYear();
        this.handleMoodList();
        this.lineVisible = true;
        setTimeout(() => {
          this.handleLine();
        }, 10)
      })
    },
    handleMoodList() {
      this.dateMoodList = new Array(7).fill(null);
      this.weekList.forEach((item, index) => {
        const obj = this.journalList.find(journal => journal.currentDate === item.fullDate);
        if (obj) this.dateMoodList[index] = obj;
      })
    },
    setCurrentMonthAndYear() {
      const di = getDateInfo(this.weekList[0].fullDate);
      this.currentMonth = monthMap[di.month - 1];
      this.currentYear = di.year;
    },
    showContent(obj) {
      if (this.modalVisible) {
        this.currentContent = obj.content;
        return;
      }
      this.modalVisible = true
      this.currentContent = obj.content
      notification.open({
        key: 1,
        description: () => this.currentContent,
        placement: 'bottomRight',
        duration: 0,
        onClick: () => {
          this.modalVisible = false;
        },
      });
    },
    handleLine() {
      const arr = Object.keys(this.$refs)
      arr.forEach((item, index) => {
        if (arr[index] && arr[index + 1] && this.$refs[arr[index]][0] && this.$refs[arr[index + 1]][0]) {
          let line = LeaderLine.setLine(this.$refs[item][0], this.$refs[arr[index + 1]][0], {
            startPlug: 'behind',
            endPlug: 'behind',
            color: '#333',
            path: 'straight',
            size: 1,
            startSocket: 'right',
            endSocket: 'left',
            startSocketGravity: 100
          })
          this.lineArr.push(line)
        }
      })
    },
    setLineVisible(visible) {
      const arr = document.querySelectorAll('.leader-line')
      if (arr && arr.length) {
        arr.forEach(item => {
          item.style.display = visible ? 'block' : 'none'
        })
      }
    },
    destroyLine() {
      this.lineArr.forEach(item => item.remove());
      this.lineArr = []
    }
  },
  activated() {
    this.setLineVisible(true)
  },
  deactivated() {
    this.setLineVisible(false)
  },
  mounted() {
    this.handleLine();
    this.setLineVisible(true)
  },
  unmounted() {
    this.setLineVisible(false)
  },
  beforeDestroy() {
    this.destroyLine();
  }
};
</script>
<style lang="less" scoped>
/* (unchanged styles) */
.analysis-journal {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 10px;
  box-sizing: border-box;
  background: #fff;
  border-radius: 10px;

  .insight-tab {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .insight-content {
    &-header {
      display: flex;
      justify-content: space-between;
      margin-top: 6px;

      .header-date {
        font-weight: bold;
        font-size: 18px;
      }
    }

    &-date {
      display: flex;

      .date-left {
        display: flex;
        flex-direction: column;
        padding: 140px 20px 0 20px;
        flex: none;
        position: relative;

        &-change-week {
          width: 75%;
          display: flex;
          justify-content: space-between;
          position: absolute;
          top: 45px;
          left: 10px;

          &-item {
            cursor: pointer;

            &:hover { opacity: 0.8; }
          }

          .disable-change {
            cursor: not-allowed;
            opacity: 0.2;
          }
        }

        &-mood-item { height: 80px; }
      }

      .date-right {
        padding-top: 20px;
        display: flex;
        justify-content: space-around;
        flex: auto;
        margin-left: 20px;
        position: relative;

        .line {
          position: absolute;
          left: 0;
          right: 0;
          width: 95%;
          height: 0.5px;
          background: rgba(0, 0, 0, 0.1);
        }

        .line1 { top: 150px; }
        .line2 { top: 230px; }
        .line3 { top: 310px; }
        .line4 { top: 390px; }
        .line5 { top: 470px; }

        .active-date {
          color: #2d7dfe;
          .date-title .date {
            color: #fff;
            border-radius: 50%;
            background-color: #2d7dfe;
          }
        }

        &-item {
          flex: 1;
          display: flex;
          flex-direction: column;

          .date-title {
            flex: none;
            height: 120px;
            padding-left: 26px;

            .day { font-size: 12px; color: rgba(0, 0, 0, 0.5); padding-left: 4px; }
            .date {
              margin-top: 10px;
              font-weight: bold;
              font-size: 18px;
              display: flex;
              align-items: center;
              justify-content: center;
              width: 28px;
              height: 28px;
            }
          }

          .mood-item {
            flex: 1;
            z-index: 9;
            position: relative;

            .active-img { background: #2d7dfe; }

            &-img {
              border-radius: 50%;
              width: 80px;
              height: 80px;
              display: flex;
              align-items: center;
              justify-content: center;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
              background: #fff;
              transform: translate(0, -45%);
              cursor: pointer;

              .mood-img {
                border-radius: 50%;
                width: 70px;
                height: 70px;

                &:hover { transform: scale(1.1); }
              }
            }
          }
        }
      }
    }
  }
}
</style>
