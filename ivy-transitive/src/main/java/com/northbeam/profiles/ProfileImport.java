package com.northbeam.profiles;

import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import org.apache.commons.beanutils.BeanUtils;

public final class ProfileImport {
    public void importFields(Object profile, Map<String, String> submittedFields)
            throws IllegalAccessException, InvocationTargetException {
        BeanUtils.populate(profile, submittedFields);
    }
}
