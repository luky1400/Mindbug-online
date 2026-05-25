import { backendUrl } from "../config";

// TODO - check if all cards are included here
const baseStrengthByName: Record<string, number> = {
  "Axolotl Healer": 4,
  "Battle Beetle": 8,
  "Bee Bear": 8,
  "Boar Zooka": 6,
  "Brain Fly": 4,
  "Bugserker": 3,
  "Chameleon Sniper": 1,
  "Compost Dragon": 3,
  "Count Draculeech": 7,
  "Creep from the Deep": 4,
  "Deathweaver": 2,
  "Elephantopus": 7,
  "Explosive Toad": 5,
  "Ferret Bomber": 2,
  "Ferret Pacifier": 4,
  "Froblin Instigator": 1,
  "Future Eric": 3,
  "Giraffodile": 7,
  "Goblin Werewolf": 2,
  "Gorillion": 10,
  "Goreagle Alpha": 6,
  "Grave Robber": 7,
  "Hamster Lion": 8,
  "Harpy Mother": 5,
  "Hungry Hungry Hamster": 2,
  "Hyenix": 7,
  "Jazz Dog": 5,
  "Kangasaurus Rex": 7,
  "Killer Bee": 5,
  "Knightmare": 5,
  "Lone Yeti": 5,
  "Luchataur": 9,
  "Macaw Dagon": 8,
  "Majestic Manticore": 6,
  "Mindbug Bug": 7,
  "Mysterious Mermaid": 7,
  "Plated Scorpion": 2,
  "Ram Hopper": 7,
  "Ratomanger": 2,
  "Rhino Turtle": 8,
  "Shark Dog": 4,
  "Sharky Crab Dog Mummypus": 5,
  "Shield Bugs": 4,
  "Short Neck Giraffodile": 7,
  "Sluggernaut": 6,
  "Snail Hydra": 9,
  "Snail Thrower": 1,
  "Spider Owl": 3,
  "Steamforger": 9,
  "Strange Barrel": 6,
  "Suspicious Gift": 1,
  "The Lurker": 4,
  "The Pack": 4,
  "Tiger Squirrel": 3,
  "Turbo Bug": 4,
  "Turf the Surfer": 8,
  "Tusked Extorter": 8,
  "Unigon": 9,
  "Urchin Hurler": 5,
  "Watts Dog": 5,
  "Wheatle": 6,
  "Wolfman Steve": 8
};

const nativeAbilityTagsByName: Record<string, string[]> = {
  "Axolotl Healer": ["POISONOUS"],
  "Chameleon Sniper": ["SNEAKY"],
  "Compost Dragon": ["HUNTER"],
  "Creep from the Deep": ["HUNTER", "POISONOUS"],
  "Deathweaver": ["POISONOUS"],
  "Explosive Toad": ["FRENZY"],
  "Ferret Bomber": ["SNEAKY"],
  "Froblin Instigator": ["HUNTER"],
  "Future Eric": ["SNEAKY"],
  "Goblin Werewolf": ["HUNTER"],
  "Goreagle Alpha": ["FRENZY", "HUNTER"],
  "Hamster Lion": ["FRENZY"],
  "Hungry Hungry Hamster": ["SNEAKY"],
  "Hyenix": ["FRENZY"],
  "Jazz Dog": ["SNEAKY"],
  "Killer Bee": ["HUNTER"],
  "Luchataur": ["FRENZY"],
  "Majestic Manticore": ["POISONOUS"],
  "Plated Scorpion": ["POISONOUS"],
  "Ram Hopper": ["FRENZY"],
  "Rhino Turtle": ["FRENZY"],
  "Shark Dog": ["HUNTER"],
  "Sluggernaut": ["TOUGH"],
  "Snail Thrower": ["POISONOUS"],
  "Spider Owl": ["SNEAKY", "POISONOUS"],
  "The Pack": ["TOUGH", "HUNTER"],
  "Tiger Squirrel": ["SNEAKY"],
  "Urchin Hurler": ["HUNTER"],
  "Watts Dog": ["FRENZY"],
  "Wheatle": ["FRENZY", "TOUGH"]
};

const highlightedBattlefieldCards = new Set([
  "Bee Bear",
  "Boar Zooka",
  "Deathweaver",
  "Elephantopus",
  "Ferret Pacifier",
  "Hamster Lion",
  "Knightmare",
  "Mindbug Bug",
  "Watts Dog",
  "Wolfman Steve"
]);

export interface ParsedCard {
  raw: string;
  name: string;
  strengthText: string;
  details: string;
  currentStrength: number | null;
  toughCharges: number | null;
  activeTags: string[];
}

export function parseCardLabel(label: string): ParsedCard {
  const raw = String(label || "").trim();
  const match = raw.match(/^(.*?)\s\[(\-?\d+)\](.*)$/);
  if (!match) {
    return {
      raw,
      name: raw,
      strengthText: "?",
      details: "",
      currentStrength: null,
      toughCharges: null,
      activeTags: []
    };
  }
  const currentStrength = Number(match[2].trim());
  const details = match[3].trim();
  const toughMatch = details.match(/tough:(\d+)/i);
  const tagsMatch = details.match(/<([^>]+)>/);
  return {
    raw,
    name: match[1].trim(),
    strengthText: match[2].trim(),
    details,
    currentStrength: Number.isFinite(currentStrength) ? currentStrength : null,
    toughCharges: toughMatch ? Number(toughMatch[1]) : null,
    activeTags: tagsMatch
      ? tagsMatch[1]
          .split(",")
          .map((tag) => tag.trim().toUpperCase())
          .filter(Boolean)
      : []
  };
}

export function cardHasTag(cardLabel: string | undefined, tag: string): boolean {
  return String(cardLabel || "").toUpperCase().includes(tag.toUpperCase());
}

export function cardImageUrl(cardLabel: string): string {
  const name = parseCardLabel(cardLabel).name;
  const slug = name
    .toLowerCase()
    .replace(/[^a-z0-9 ]+/g, "")
    .trim()
    .replace(/\s+/g, "_");
  return backendUrl(`/card-images/${slug}.png`);
}

export function strengthClassName(cardLabel: string): "buff" | "debuff" | "neutral" {
  const parsed = parseCardLabel(cardLabel);
  if (parsed.currentStrength === null) return "neutral";
  const base = baseStrengthByName[parsed.name];
  if (!Number.isFinite(base)) return "neutral";
  if (parsed.currentStrength > base) return "buff";
  if (parsed.currentStrength < base) return "debuff";
  return "neutral";
}

export function hasActiveToughCharge(cardLabel: string): boolean {
  const parsed = parseCardLabel(cardLabel);
  return Boolean(parsed.toughCharges && parsed.toughCharges > 0);
}

export function getActiveAbilityBadges(cardLabel: string): string[] {
  const parsed = parseCardLabel(cardLabel);
  const nativeTags = nativeAbilityTagsByName[parsed.name] || [];
  const effectGrantedVisibleTags = ["FRENZY", "HUNTER", "POISONOUS", "SNEAKY"];
  return effectGrantedVisibleTags.filter(
    (tag) => parsed.activeTags.includes(tag) && !nativeTags.includes(tag)
  );
}

export function isHighlightedBattlefieldCard(cardLabel: string): boolean {
  return highlightedBattlefieldCards.has(parseCardLabel(cardLabel).name);
}
