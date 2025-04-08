// This file is used to declare modules for image files.
// This allows TypeScript to understand how to handle imports for these file types.
declare module '*.png' {
    const value: string;
    export default value;
}

declare module '*.svg' {
    const value: string;
    export default value;
}