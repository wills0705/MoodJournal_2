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

// 获取当天的年，月，日
const dateInfo = getDateInfo(new Date());
export default {
  name: 'analysis',
  components: {
    LeftCircleOutlined,
    RightCircleOutlined,
  },
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
      // 当前月份
      currentMonth: monthMap[dateInfo.month - 1],
      // 当前年份
      currentYear: dateInfo.year,
      // 当前日期,yyyy-mm-dd
      currentDate: dateInfo.fullDate,
      // 当前的年月日， yyyy-mm-dd
      currentFormatDate: formatDate(new Date()),
      // 获取当前一周的起止日期
      weekList: getWeekDates(0),
      // 心情日记列表，status = 0 = great, 1= good, 2= neutral, 3=mooday, 4=down
      dateMoodList: [

      ],
      // 心情文本
      moodList: [
        'Great',
        'Good',
        'Neutral',
        'Mooday',
        'Down'
      ],
      // 弹窗显示隐藏，展示日记内容
      modalVisible: false,
      // 当前展示的日记内容
      currentContent: '',
      // 周的索引，0=当前周，1=下一周，-1=上一周
      weekIndex: 0,
      // 默认连线是否显示
      lineVisible: true,
      // 连线集合
      lineArr: [],
    }
  },
  methods: {
    // flag > 1 = 下一周， flag < 1 = 上一周
    handleWeekChange(flag) {
      if (flag > 0) {
        if (this.weekIndex === 0) {
          return;
        }
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
        if (obj) {
          this.dateMoodList[index] = obj;
        }
      })
    },
    // 设置显示的年月
    setCurrentMonthAndYear() {
      const dateInfo = getDateInfo(this.weekList[0].fullDate);
      this.currentMonth = monthMap[dateInfo.month - 1];
      this.currentYear = dateInfo.year;
    },
    // 打开右下角弹窗，并展示日记内容
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
    // 使用leader-line-vue处理连线
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
            startSocket: 'right', // 自动定位起始元素的中心
            endSocket: 'left',   // 自动定位结束元素的中心
            startSocketGravity: 100
          })
          this.lineArr.push(line)
        }
      })
    },
    handleLinePosition(arr) {
      let result = [];
      arr.forEach((item, index) => {
        let p = ['left', 'left']
        const val = this.dateMoodList[index + 1].status - this.dateMoodList[index]
        if (index === 0) {
          switch (val) {
            case 0:
              p = ['right', 'left']
            case 1 || 2:
              p = ['left', 'left']
            case 3 || 4:
              p = ['bottom', 'left']
            case -4:
              p = ['top', 'left']
            case -1:
              p = ['right', 'top']
            case -2:
              p = ['top', 'top']
          }
        } else {
          switch (val) {
            case 0:
              p = ['right', 'left']
            case 1 || 2:
              p = ['left', 'left']
            case 3 || 4:
              p = ['bottom', 'left']
            case -4:
              p = ['top', 'left']
          }
        }

      })
    },
    // 切换tab时，显示或者隐藏连线
    setLineVisible(visible) {
      const arr = document.querySelectorAll('.leader-line')
      if (arr && arr.length) {
        arr.forEach(item => {
          item.style.display = visible ? 'block' : 'none'
        })
      }
    },
    destroyLine() {
      this.lineArr.forEach(item => {
        item.remove()
      })
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

            &:hover {
              opacity: 0.8;
            }
          }

          .disable-change {
            cursor: not-allowed;
            opacity: 0.2;
          }
        }

        &-mood-item {
          height: 80px;
        }
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

        .line1 {
          top: 150px;
        }

        .line2 {
          top: 230px;
        }

        .line3 {
          top: 310px;
        }

        .line4 {
          top: 390px;
        }

        .line5 {
          top: 470px;
        }

        .active-date {
          color: #2d7dfe;

          .date-title {
            .date {

              color: #fff;
              border-radius: 50%;
              background-color: #2d7dfe;
            }
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

            .day {
              font-size: 12px;
              color: rgba(0, 0, 0, 0.5);
              padding-left: 4px;
            }

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

            .active-img {
              background: #2d7dfe;
            }

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

                &:hover {
                  transform: scale(1.1);
                }
              }
            }
          }
        }
      }
    }
  }
}
</style>
