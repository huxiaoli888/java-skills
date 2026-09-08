package com.chaken.ai.test.architecture;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

@AnalyzeClasses(packages = "com.chaken.ai.test", importOptions = ImportOption.DoNotIncludeTests.class)
class LayerDependencyArchTest {
    @ArchTest
    static final ArchRule common_must_not_depend_on_business_modules = noClasses()
            .that().resideInAPackage("..common..")
            .should().dependOnClassesThat().resideInAnyPackage("..cms..", "..sdk..", "..infrastructure..")
            .allowEmptyShould(true);

    @ArchTest
    static final ArchRule infrastructure_must_not_depend_on_api_modules = noClasses()
            .that().resideInAPackage("..infrastructure..")
            .should().dependOnClassesThat().resideInAnyPackage("..cms..", "..sdk..")
            .allowEmptyShould(true);

    @ArchTest
    static final ArchRule api_modules_must_not_depend_on_each_other = noClasses()
            .that().resideInAPackage("..cms..")
            .should().dependOnClassesThat().resideInAPackage("..sdk..")
            .allowEmptyShould(true);
}
