package com.chaken.ai.test.architecture;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

@AnalyzeClasses(packages = "com.chaken.ai.test", importOptions = ImportOption.DoNotIncludeTests.class)
class ControllerContractArchTest {
    @ArchTest
    static final ArchRule controllers_should_not_depend_on_entities = noClasses()
            .that().resideInAPackage("..controller..")
            .should().dependOnClassesThat().resideInAPackage("..entity..")
            .allowEmptyShould(true);

    @ArchTest
    static final ArchRule request_dto_should_not_depend_on_services = noClasses()
            .that().haveSimpleNameEndingWith("Request")
            .or().haveSimpleNameEndingWith("Query")
            .should().dependOnClassesThat().resideInAPackage("..service..")
            .allowEmptyShould(true);

    @ArchTest
    static final ArchRule controllers_should_have_controller_suffix = classes()
            .that().areAnnotatedWith("org.springframework.web.bind.annotation.RestController")
            .should().haveSimpleNameEndingWith("Controller")
            .allowEmptyShould(true);
}
