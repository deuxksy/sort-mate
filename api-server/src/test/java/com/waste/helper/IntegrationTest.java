package com.waste.helper;

import com.waste.helper.config.AsyncSyncConfiguration;
import com.waste.helper.config.DatabaseTestcontainer;
import com.waste.helper.config.JacksonConfiguration;
import com.waste.helper.config.RedisTestContainer;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.context.ImportTestcontainers;

/**
 * Base composite annotation for integration tests.
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@SpringBootTest(
    classes = {
        WasteHelperApp.class,
        JacksonConfiguration.class,
        AsyncSyncConfiguration.class,
        com.waste.helper.config.JacksonHibernateConfiguration.class,
    }
)
@ImportTestcontainers({ DatabaseTestcontainer.class, RedisTestContainer.class })
public @interface IntegrationTest {}
