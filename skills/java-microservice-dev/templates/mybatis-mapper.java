package {{basePackage}}.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import {{basePackage}}.entity.{{entityClass}};

@Mapper
public interface {{mapperClass}} {

    {{entityClass}} selectById(@Param("id") Long id);

    int insert({{entityClass}} entity);

    int updateById({{entityClass}} entity);
}
