// OMNI MOTHER — Zod Type Stub
// Minimal type declarations for zod schema validation library
// Production stubs for ecosystem integrity when npm install is unavailable

declare module "zod" {
    export interface ZodType<Output = any, Def extends ZodTypeDef = ZodTypeDef, Input = Output> {
        parse(data: unknown): Output;
        safeParse(data: unknown): SafeParseReturnType<Input, Output>;
        optional(): ZodOptional<this>;
        nullable(): ZodNullable<this>;
        array(): ZodArray<this>;
        describe(description: string): this;
    }

    export interface ZodTypeDef {}

    export type SafeParseReturnType<Input, Output> =
        | { success: true; data: Output }
        | { success: false; error: ZodError };

    export class ZodError extends Error {
        issues: ZodIssue[];
    }

    export interface ZodIssue {
        code: string;
        message: string;
        path: (string | number)[];
    }

    export interface ZodString extends ZodType<string> {
        min(min: number, message?: string): ZodString;
        max(max: number, message?: string): ZodString;
        email(message?: string): ZodString;
        url(message?: string): ZodString;
        uuid(message?: string): ZodString;
        regex(regex: RegExp, message?: string): ZodString;
    }

    export interface ZodNumber extends ZodType<number> {
        min(min: number, message?: string): ZodNumber;
        max(max: number, message?: string): ZodNumber;
        int(message?: string): ZodNumber;
        positive(message?: string): ZodNumber;
        negative(message?: string): ZodNumber;
    }

    export interface ZodBoolean extends ZodType<boolean> {}

    export interface ZodArray<T extends ZodType> extends ZodType<T["_output"][]> {
        min(min: number, message?: string): ZodArray<T>;
        max(max: number, message?: string): ZodArray<T>;
        nonempty(message?: string): ZodArray<T>;
    }

    export interface ZodObject<Shape extends Record<string, ZodType>> extends ZodType<{ [K in keyof Shape]: Shape[K]["_output"] }> {
        shape: Shape;
        extend<Augmentation extends Record<string, ZodType>>(augmentation: Augmentation): ZodObject<Shape & Augmentation>;
        merge<Incoming extends ZodObject<any>>(merging: Incoming): ZodObject<Shape & Incoming["shape"]>;
        pick<Mask extends { [K in keyof Shape]?: true }>(mask: Mask): ZodObject<Pick<Shape, Extract<keyof Shape, keyof Mask>>>;
        omit<Mask extends { [K in keyof Shape]?: true }>(mask: Mask): ZodObject<Omit<Shape, keyof Mask>>;
        partial(): ZodObject<{ [K in keyof Shape]: ZodOptional<Shape[K]> }>;
    }

    export interface ZodOptional<T extends ZodType> extends ZodType<T["_output"] | undefined> {}
    export interface ZodNullable<T extends ZodType> extends ZodType<T["_output"] | null> {}

    export interface ZodEnum<T extends [string, ...string[]]> extends ZodType<T[number]> {}

    export interface ZodUnion<T extends readonly ZodType[]> extends ZodType<T[number]["_output"]> {}

    export interface ZodRecord<Key extends ZodType<string>, Value extends ZodType> extends ZodType<Record<Key["_output"], Value["_output"]>> {}

    export interface ZodTuple<T extends ZodType[]> extends ZodType<{ [K in keyof T]: T[K]["_output"] }> {}

    export interface ZodLiteral<T> extends ZodType<T> {}

    export const z: {
        string(): ZodString;
        number(): ZodNumber;
        boolean(): ZodBoolean;
        object<Shape extends Record<string, ZodType>>(shape: Shape): ZodObject<Shape>;
        array<T extends ZodType>(schema: T): ZodArray<T>;
        enum<T extends [string, ...string[]]>(values: T): ZodEnum<T>;
        union<T extends readonly [ZodType, ZodType, ...ZodType[]]>(types: T): ZodUnion<T>;
        record<Value extends ZodType>(valueSchema: Value): ZodRecord<ZodString, Value>;
        tuple<T extends [ZodType, ...ZodType[]]>(schemas: T): ZodTuple<T>;
        literal<T extends string | number | boolean>(value: T): ZodLiteral<T>;
        any(): ZodType<any>;
        unknown(): ZodType<unknown>;
        void(): ZodType<void>;
        never(): ZodType<never>;
        null(): ZodType<null>;
        undefined(): ZodType<undefined>;
        date(): ZodType<Date>;
        optional<T extends ZodType>(schema: T): ZodOptional<T>;
        nullable<T extends ZodType>(schema: T): ZodNullable<T>;
        infer: any;
    };

    export type infer<T extends ZodType> = T["_output"];

    export default z;
}
