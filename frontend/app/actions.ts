"use server";

import { revalidatePath } from "next/cache";

import { refreshHomepageSelection } from "@/lib/startup-store";

export async function refreshHomepageAction() {
  await refreshHomepageSelection();
  revalidatePath("/");
}
