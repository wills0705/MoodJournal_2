const monthMap = {
  0: "January", 1: "February", 2: "March", 3: "April",
  4: "May", 5: "June", 6: "July", 7: "August",
  8: "September", 9: "October", 10: "November", 11: "December",
};

const dayMap = {
  0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
  4: "Thursday", 5: "Friday", 6: "Saturday",
};

const weekDayMap = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];


function parseYMDLocal(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  if (!m) return new Date(s);
  return new Date(+m[1], +m[2] - 1, +m[3]); // local
}

function toLocalDate(input) {
  if (!input) return new Date();
  if (input instanceof Date) return new Date(input.getTime());
  if (typeof input === "string" && /^\d{4}-\d{2}-\d{2}$/.test(input)) {
    return parseYMDLocal(input);
  }
  return new Date(input);
}

function atLocalMidnight(d) {
  const x = toLocalDate(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

function formatDate(date) {
  const d = atLocalMidnight(date);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function getDateInfo(dd) {
  const d = atLocalMidnight(dd);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const date = String(d.getDate()).padStart(2, "0");
  const fullDate = `${year}-${month}-${date}`;
  return { year, month, date, fullDate };
}

function getWeekDates(weekIndex) {
  // Use date arithmetic (setDate) to avoid DST/ms-offset surprises
  const base = atLocalMidnight(new Date());
  base.setDate(base.getDate() + (weekIndex || 0) * 7);

  // Start from Sunday of that week
  const start = atLocalMidnight(base);
  start.setDate(start.getDate() - start.getDay()); // Sunday = 0

  const dates = [];
  for (let i = 0; i < 7; i++) {
    const day = atLocalMidnight(start);
    day.setDate(start.getDate() + i);
    dates.push({
      day: weekDayMap[day.getDay()],           // label from actual day
      date: String(day.getDate()).padStart(2, "0"),
      fullDate: getDateInfo(day).fullDate,
    });
  }
  return dates;
}

export { formatDate, getDateInfo, monthMap, dayMap, getWeekDates };
