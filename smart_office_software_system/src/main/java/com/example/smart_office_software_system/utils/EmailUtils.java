package com.example.smart_office_software_system.utils;

import lombok.extern.slf4j.Slf4j;

import javax.naming.Context;
import javax.naming.NamingException;
import javax.naming.directory.Attribute;
import javax.naming.directory.Attributes;
import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;
import java.util.Hashtable;

@Slf4j
public class EmailUtils {
    /**
     * 判断邮箱号是否存在
     * @param email
     * @return
     */
    public static boolean isEmailValid(String email) {
        String domain = email.substring(email.indexOf("@") + 1);
        try {
            Hashtable<String, Object> env = new Hashtable<>();
            env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.dns.DnsContextFactory");
            DirContext ctx = new InitialDirContext(env);
            Attributes attrs = ctx.getAttributes(domain, new String[]{"MX"});
            Attribute mxAttr = attrs.get("MX");

            if (mxAttr != null) {
                return true; // 邮箱域名的 MX 记录存在，说明邮箱号可能存在
            } else {
                log.info("邮箱域名的 MX 记录不存在，说明邮箱号不存在");
                return false; // 邮箱域名的 MX 记录不存在，说明邮箱号不存在
            }
        } catch (NamingException e) {
            log.info("出现异常，邮箱号可能不存在");
            return false; // 出现异常，邮箱号可能不存在
        }
    }
}
