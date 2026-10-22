export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export type Dish = {
  id: string;
  name: string;
};

export type DayMenu = {
  breakfast: Dish[];
  lunch: Dish[];
  dinner: Dish[];
  snack: Dish[];
};

export type MenuStore = Record<string, DayMenu>;

export const MEAL_ORDER: MealType[] = [
  "breakfast",
  "lunch",
  "dinner",
  "snack",
];

export const MEAL_LABELS: Record<MealType, string> = {
  breakfast: "早餐",
  lunch: "午餐",
  dinner: "晚餐",
  snack: "加餐",
};

export const MEAL_HINTS: Record<MealType, string> = {
  breakfast: "清淡开胃，开启一天",
  lunch: "主食搭配，吃饱又舒服",
  dinner: "暖胃收工，别太油重",
  snack: "水果、坚果或一杯茶",
};

const STORAGE_KEY = "daily-menu:v1";

export function emptyDay(): DayMenu {
  return { breakfast: [], lunch: [], dinner: [], snack: [] };
}

export function dateKey(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function parseDateKey(key: string): Date {
  const [y, m, d] = key.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function addDays(date: Date, delta: number): Date {
  const next = new Date(date);
  next.setDate(next.getDate() + delta);
  return next;
}

export function formatDisplayDate(date: Date): string {
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  }).format(date);
}

export function isSameDay(a: Date, b: Date): boolean {
  return dateKey(a) === dateKey(b);
}

export function createDish(name: string): Dish {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    name: name.trim(),
  };
}

export function loadStore(): MenuStore {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as MenuStore;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

export function saveStore(store: MenuStore): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

export function sampleDay(): DayMenu {
  return {
    breakfast: [
      createDish("小米粥"),
      createDish("茶叶蛋"),
      createDish("凉拌黄瓜"),
    ],
    lunch: [
      createDish("番茄牛腩面"),
      createDish("蒜蓉西兰花"),
    ],
    dinner: [
      createDish("清蒸鲈鱼"),
      createDish("蚝油生菜"),
      createDish("米饭"),
    ],
    snack: [createDish("时令水果")],
  };
}

export function dishCount(day: DayMenu): number {
  return MEAL_ORDER.reduce((sum, meal) => sum + day[meal].length, 0);
}
