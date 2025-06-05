// 月份映射
const monthMap = {
  0: "January",
  1: "February",
  2: "March",
  3: "April",
  4: "May",
  5: "June",
  6: "July",
  7: "August",
  8: "September",
  9: "October",
  10: "November",
  11: "December",
};

// 一周每天的映射
const dayMap = {
  1: "Monday",
  2: "TuesDay",
  3: "WednesDay",
  4: "ThursDay",
  5: "Friday",
  6: "SaturDay",
  7: "Sunday",
};

// 一周每天的映射，取前三个字符
const weekDayMap = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// 格式化日期，输出yyyy-mm-dd
function formatDate(date) {
  const d = new Date(date || "");
  let month = "" + (d.getMonth() + 1);
  let day = "" + d.getDate();
  let year = d.getFullYear();

  if (month.length < 2) month = "0" + month;
  if (day.length < 2) day = "0" + day;

  return [year, month, day].join("-");
}

// 获取当前的年，月，日
function getDateInfo(dd) {
  const d = new Date(dd);
  let month = "" + (d.getMonth() + 1);
  let date = "" + d.getDate();
  let year = d.getFullYear();

  if (month.length < 2) month = "0" + month;
  if (date.length < 2) date = "0" + date;
  let fullDate = `${year}-${month}-${date}`;
  return {
    year,
    month,
    date,
    fullDate,
  };
}

// 获取今天所在的周，以及周一到周日对应的日期

function getWeekDates(weekIndex) {
  const today = new Date(new Date().getTime() + 7 * 24 * 60 * 60 * 1000 * weekIndex);
  const startDayOfWeek = today.getDate() - today.getDay(); // 计算本周第一天（周日）的日期
  const dates = [];
  for (let i = 0; i < 7; i++) {
    // 创建一个新的Date对象，表示当前周的每一天
    const day = new Date(
      today.getFullYear(),
      today.getMonth(),
      startDayOfWeek + i
    );
    // 将日期格式化为 "DD" 格式
    const dateOfMonth = day.getDate().toString().padStart(2, "0");
    dates.push({
      day: weekDayMap[i],
      date: dateOfMonth,
      fullDate: getDateInfo(day).fullDate,
    });
  }
  return dates;
}

export { formatDate, getDateInfo, monthMap, dayMap, getWeekDates };
