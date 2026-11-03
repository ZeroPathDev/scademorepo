package com.northbeam.collections;

import java.util.Collection;
import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.InvokerTransformer;

public final class CollectionIntake {
    public Collection transform(Collection values, String requestedMethod) {
        Transformer transformer = new InvokerTransformer(requestedMethod, null, null);
        return CollectionUtils.collect(values, transformer);
    }
}
