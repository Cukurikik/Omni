// OMNI MOTHER: Enka.network TypeScript Interfaces (Production Grade)
// Comprehensive type definitions mapping the Enka API response schema.
// Ensures strict type safety across the frontend and caching layers.

export interface EnkaProp {
    type: number;
    ival: string;
    val?: string;
}

export interface EnkaFlatReliquary {
    nameTextMapHash: string;
    setNameTextMapHash: string;
    rankLevel: number;
    reliquaryMainstat: {
        mainPropId: string;
        statValue: number;
    };
    reliquarySubstats?: Array<{
        appendPropId: string;
        statValue: number;
    }>;
    itemType: string;
    icon: string;
    equipType: string;
}

export interface EnkaWeapon {
    itemId: number;
    weapon: {
        level: number;
        promoteLevel: number;
        affixMap: Record<string, number>;
    };
    flat: {
        nameTextMapHash: string;
        rankLevel: number;
        weaponStats: Array<{
            appendPropId: string;
            statValue: number;
        }>;
        icon: string;
    };
}

export interface EnkaReliquary {
    itemId: number;
    reliquary: {
        level: number;
        mainPropId: number;
        appendPropIdList: number[];
    };
    flat: EnkaFlatReliquary;
}

export interface EnkaAvatarInfo {
    avatarId: number;
    propMap: Record<string, EnkaProp>;
    fightPropMap: Record<string, number>;
    skillDepotId: number;
    inherentProudSkillList: number[];
    skillLevelMap: Record<string, number>;
    proudSkillExtraLevelMap?: Record<string, number>;
    equipList: Array<EnkaWeapon | EnkaReliquary>;
    fetterInfo: {
        expLevel: number;
    };
    costumes?: number[];
}

export interface EnkaPlayerInfo {
    nickname: string;
    level: number;
    signature?: string;
    worldLevel: number;
    nameCardId: number;
    finishAchievementNum: number;
    towerFloorIndex: number;
    towerLevelIndex: number;
    showAvatarInfoList: Array<{
        avatarId: number;
        level: number;
    }>;
    showNameCardIdList: number[];
    profilePicture: {
        avatarId: number;
    };
}

export interface EnkaResponse {
    playerInfo: EnkaPlayerInfo;
    avatarInfoList?: EnkaAvatarInfo[];
    ttl: number;
    uid: string;
}

export class EnkaApiError extends Error {
    constructor(public statusCode: number, message: string) {
        super(message);
        this.name = "EnkaApiError";
    }
}
