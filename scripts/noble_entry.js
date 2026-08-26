import { gcm } from '@noble/ciphers/aes.js';
import { pbkdf2 } from '@noble/hashes/pbkdf2.js';
import { sha256 } from '@noble/hashes/sha2.js';

export function decryptVault(VAULT, username, password) {
  const userKeyNormalized = (username || '').trim().toLowerCase();
  const uinfo = VAULT.users[userKeyNormalized];
  if (!uinfo) throw new Error('Usuário corporativo não autorizado.');

  function b64ToBytes(b64) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return bytes;
  }

  function bytesToB64(bytes) {
    let bin = '';
    for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin);
  }

  const saltBytes = b64ToBytes(uinfo.salt);
  const ivBytes = b64ToBytes(uinfo.iv);
  const wrappedKeyBytes = b64ToBytes(uinfo.wrapped_key);

  const enc = new TextEncoder();
  const passBytes = enc.encode(password);

  // 1. PBKDF2 SHA256 100,000 iterations
  const userKey = pbkdf2(sha256, passBytes, saltBytes, { c: 100000, dkLen: 32 });

  // 2. Decrypt Master Key with AES-GCM
  let masterKey;
  try {
    const cipherUser = gcm(userKey, ivBytes);
    masterKey = cipherUser.decrypt(wrappedKeyBytes);
  } catch (err) {
    throw new Error('Senha incorreta. Verifique suas credenciais.');
  }

  // 3. Decrypt Payload
  const dataIvBytes = b64ToBytes(VAULT.data_iv);
  const encDataBytes = b64ToBytes(VAULT.encrypted_data);

  const cipherData = gcm(masterKey, dataIvBytes);
  const decryptedBytes = cipherData.decrypt(encDataBytes);

  const dec = new TextDecoder();
  const payload = JSON.parse(dec.decode(decryptedBytes));
  return { payload, uinfo, masterKeyRawB64: bytesToB64(masterKey) };
}

export function decryptSession(VAULT, masterKeyRawB64) {
  function b64ToBytes(b64) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return bytes;
  }

  const masterKey = b64ToBytes(masterKeyRawB64);
  const dataIvBytes = b64ToBytes(VAULT.data_iv);
  const encDataBytes = b64ToBytes(VAULT.encrypted_data);

  const cipherData = gcm(masterKey, dataIvBytes);
  const decryptedBytes = cipherData.decrypt(encDataBytes);

  const dec = new TextDecoder();
  return JSON.parse(dec.decode(decryptedBytes));
}
