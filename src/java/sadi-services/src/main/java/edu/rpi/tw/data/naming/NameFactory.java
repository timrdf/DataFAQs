package edu.rpi.tw.data.naming;

import java.io.UnsupportedEncodingException;
import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Some methods copied from csv2rdf4lod's NameFactory.
 */
public class NameFactory {
	/**
	 * 
	 * @param value
	 * @return the a hash (e.g. MD5) of the given 'value'
	 */
	public static String getMD5(String value) {
		byte[] bytesOfMessage;
		String hashtext = null;
		try {
			// http://stackoverflow.com/questions/415953/generate-md5-hash-in-java
			bytesOfMessage = (value).getBytes("UTF-8");
			MessageDigest md = MessageDigest.getInstance("MD5");
			byte[] digest = md.digest(bytesOfMessage);
			BigInteger bigInt = new BigInteger(1,digest);
			hashtext = bigInt.toString(16);
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
		} catch (NoSuchAlgorithmException e) {
			e.printStackTrace();
		}
		return hashtext;
	}
}