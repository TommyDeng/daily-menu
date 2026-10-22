"use client";

import { useEffect, useState, useTransition } from "react";
import { ChevronLeft, ChevronRight, Plus, Trash2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  MEAL_HINTS,
  MEAL_LABELS,
  MEAL_ORDER,
  type DayMenu,
  type MealType,
  type MenuStore,
  addDays,
  createDish,
  dateKey,
  dishCount,
  emptyDay,
  formatDisplayDate,
  isSameDay,
  loadStore,
  parseDateKey,
  sampleDay,
  saveStore,
} from "@/lib/menu";

export function DailyMenuApp() {
  const [ready, setReady] = useState(false);
  const [store, setStore] = useState<MenuStore>({});
  const [selectedKey, setSelectedKey] = useState("");
  const [todayKey, setTodayKey] = useState("");
  const [dialogMeal, setDialogMeal] = useState<MealType | null>(null);
  const [draftName, setDraftName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  useEffect(() => {
    const loaded = loadStore();
    const today = dateKey(new Date());
    if (!loaded[today]) {
      loaded[today] = sampleDay();
      saveStore(loaded);
    }
    setStore(loaded);
    setTodayKey(today);
    setSelectedKey(today);
    setReady(true);
  }, []);

  if (!ready || !selectedKey) {
    return (
      <div className="flex min-h-full flex-1 items-center justify-center px-6">
        <p className="font-display text-2xl text-[var(--ink)]/60 animate-pulse">
          正在打开今日菜单…
        </p>
      </div>
    );
  }

  const selectedDate = parseDateKey(selectedKey);
  const today = parseDateKey(todayKey || selectedKey);
  const day: DayMenu = store[selectedKey] ?? emptyDay();
  const total = dishCount(day);

  function persist(next: MenuStore) {
    setStore(next);
    saveStore(next);
  }

  function updateDay(updater: (current: DayMenu) => DayMenu) {
    const current = store[selectedKey] ?? emptyDay();
    const nextDay = updater(current);
    persist({ ...store, [selectedKey]: nextDay });
  }

  function shiftDay(delta: number) {
    startTransition(() => {
      setSelectedKey(dateKey(addDays(selectedDate, delta)));
      setError(null);
    });
  }

  function goToday() {
    startTransition(() => {
      setSelectedKey(todayKey);
      setError(null);
    });
  }

  function openAdd(meal: MealType) {
    setDialogMeal(meal);
    setDraftName("");
    setError(null);
  }

  function submitDish() {
    const name = draftName.trim();
    if (!name) {
      setError("请输入菜名");
      return;
    }
    if (!dialogMeal) return;
    updateDay((current) => ({
      ...current,
      [dialogMeal]: [...current[dialogMeal], createDish(name)],
    }));
    setDialogMeal(null);
    setDraftName("");
    setError(null);
  }

  function removeDish(meal: MealType, id: string) {
    updateDay((current) => ({
      ...current,
      [meal]: current[meal].filter((dish) => dish.id !== id),
    }));
  }

  function fillSample() {
    persist({ ...store, [selectedKey]: sampleDay() });
  }

  function clearDay() {
    persist({ ...store, [selectedKey]: emptyDay() });
  }

  return (
    <div className="relative flex min-h-full flex-1 flex-col overflow-hidden">
      <div className="pointer-events-none absolute inset-0 atmosphere" aria-hidden />
      <div className="pointer-events-none absolute -top-24 right-[-10%] h-[28rem] w-[28rem] rounded-full bg-[radial-gradient(circle,rgba(214,122,74,0.22),transparent_68%)] blur-2xl animate-drift" aria-hidden />
      <div className="pointer-events-none absolute bottom-[-8%] left-[-12%] h-[24rem] w-[24rem] rounded-full bg-[radial-gradient(circle,rgba(74,122,96,0.2),transparent_70%)] blur-2xl animate-drift-slow" aria-hidden />

      <header className="relative z-10 mx-auto flex w-full max-w-3xl items-center justify-between px-5 pt-6 sm:px-8 sm:pt-8">
        <p className="font-display text-lg tracking-wide text-[var(--ink)] sm:text-xl">
          每日菜单
        </p>
        <Button
          variant="ghost"
          size="sm"
          onClick={goToday}
          className="text-[var(--ink-soft)] hover:bg-white/40 hover:text-[var(--ink)]"
        >
          回到今天
        </Button>
      </header>

      <main className="relative z-10 mx-auto flex w-full max-w-3xl flex-1 flex-col px-5 pb-16 pt-8 sm:px-8 sm:pt-12">
        <section className="animate-rise">
          <p className="font-display text-5xl leading-none tracking-tight text-[var(--ink)] sm:text-7xl">
            每日菜单
          </p>
          <p className="mt-4 max-w-md text-base leading-relaxed text-[var(--ink-soft)] sm:text-lg">
            为今天的三餐排好序，少纠结、多吃好。菜谱存在本机，随时改随时看。
          </p>

          <div className="mt-8 flex items-center gap-2 sm:gap-3">
            <Button
              variant="outline"
              size="icon"
              aria-label="前一天"
              onClick={() => shiftDay(-1)}
              className="border-[var(--line)] bg-white/50 text-[var(--ink)] hover:bg-white/80"
            >
              <ChevronLeft className="size-4" />
            </Button>
            <div className="min-w-0 flex-1 text-center">
              <p className="truncate font-display text-xl text-[var(--ink)] sm:text-2xl">
                {formatDisplayDate(selectedDate)}
              </p>
              <p className="mt-1 text-sm text-[var(--ink-muted)]">
                {isSameDay(selectedDate, today)
                  ? total === 0
                    ? "今天还是空的，先加几道菜吧"
                    : `今天共 ${total} 道菜`
                  : total === 0
                    ? "这一天还没有安排"
                    : `共 ${total} 道菜`}
              </p>
            </div>
            <Button
              variant="outline"
              size="icon"
              aria-label="后一天"
              onClick={() => shiftDay(1)}
              className="border-[var(--line)] bg-white/50 text-[var(--ink)] hover:bg-white/80"
            >
              <ChevronRight className="size-4" />
            </Button>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            <Button
              onClick={() => openAdd("lunch")}
              className="bg-[var(--leaf)] text-white hover:bg-[var(--leaf-deep)]"
            >
              <Plus className="size-4" />
              添加菜品
            </Button>
            {total === 0 ? (
              <Button
                variant="outline"
                onClick={fillSample}
                className="border-[var(--line)] bg-white/50 text-[var(--ink)] hover:bg-white/80"
              >
                <Sparkles className="size-4" />
                填入示例菜单
              </Button>
            ) : (
              <Button
                variant="ghost"
                onClick={clearDay}
                className="text-[var(--ink-muted)] hover:bg-white/40 hover:text-[var(--ink)]"
              >
                清空这一天
              </Button>
            )}
          </div>
        </section>

        <section className="mt-12 space-y-10 sm:mt-16">
          {MEAL_ORDER.map((meal, index) => {
            const dishes = day[meal];
            return (
              <div
                key={meal}
                className="animate-rise border-t border-[var(--line)] pt-6"
                style={{ animationDelay: `${120 + index * 70}ms` }}
              >
                <div className="flex items-end justify-between gap-4">
                  <div>
                    <h2 className="font-display text-2xl text-[var(--ink)] sm:text-3xl">
                      {MEAL_LABELS[meal]}
                    </h2>
                    <p className="mt-1 text-sm text-[var(--ink-muted)]">
                      {MEAL_HINTS[meal]}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => openAdd(meal)}
                    className="shrink-0 text-[var(--leaf)] hover:bg-[var(--leaf)]/10 hover:text-[var(--leaf-deep)]"
                  >
                    <Plus className="size-4" />
                    添加
                  </Button>
                </div>

                {dishes.length === 0 ? (
                  <button
                    type="button"
                    onClick={() => openAdd(meal)}
                    className="mt-4 w-full py-6 text-left text-[var(--ink-muted)] transition-colors hover:text-[var(--ink-soft)]"
                  >
                    还没有菜品，点这里添加
                  </button>
                ) : (
                  <ul className="mt-4 divide-y divide-[var(--line)]">
                    {dishes.map((dish) => (
                      <li
                        key={dish.id}
                        className="group flex items-center justify-between gap-3 py-3"
                      >
                        <span className="text-base text-[var(--ink)] sm:text-lg">
                          {dish.name}
                        </span>
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          aria-label={`删除 ${dish.name}`}
                          onClick={() => removeDish(meal, dish.id)}
                          className="opacity-60 text-[var(--ink-muted)] hover:bg-red-50 hover:text-red-700 sm:opacity-0 sm:group-hover:opacity-100"
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            );
          })}
        </section>
      </main>

      <Dialog
        open={dialogMeal !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDialogMeal(null);
            setError(null);
          }
        }}
      >
        <DialogContent className="border-[var(--line)] bg-[var(--paper)] sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="font-display text-2xl text-[var(--ink)]">
              添加{dialogMeal ? MEAL_LABELS[dialogMeal] : ""}菜品
            </DialogTitle>
            <DialogDescription className="text-[var(--ink-muted)]">
              写一道菜名即可，例如「番茄炒蛋」。
            </DialogDescription>
          </DialogHeader>
          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              submitDish();
            }}
          >
            <Input
              autoFocus
              value={draftName}
              onChange={(event) => {
                setDraftName(event.target.value);
                if (error) setError(null);
              }}
              placeholder="菜名"
              className="h-11 border-[var(--line)] bg-white/70 text-[var(--ink)]"
            />
            {error ? (
              <p className="text-sm text-red-700" role="alert">
                {error}
              </p>
            ) : null}
            <DialogFooter className="gap-2 sm:gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setDialogMeal(null)}
                className="text-[var(--ink-muted)]"
              >
                取消
              </Button>
              <Button
                type="submit"
                className="bg-[var(--leaf)] text-white hover:bg-[var(--leaf-deep)]"
              >
                保存
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
