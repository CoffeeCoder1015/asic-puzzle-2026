/** Resolve a public file under the build's deployment path. */
export function publicAsset(path: `/${string}`): string {
  return `${process.env.NEXT_PUBLIC_BASE_PATH}${path}`;
}
