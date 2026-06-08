cmake_minimum_required(VERSION 3.15...3.29)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
    Python
    COMPONENTS Interpreter Development.Module ${SKBUILD_SABI_COMPONENT} NumPy
    REQUIRED
)

set(PYX_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/pycocotools/_mask.pyx")
set(GENERATED_C "${CMAKE_CURRENT_BINARY_DIR}/_mask.c")

add_custom_command(
    OUTPUT "${GENERATED_C}"
    MAIN_DEPENDENCY "${PYX_SOURCE}"
    VERBATIM
    COMMAND Python::Interpreter -m cython "${PYX_SOURCE}" --output-file "${GENERATED_C}"
    COMMENT "Generating C source from _mask.pyx"
)

if(NOT "${SKBUILD_SABI_VERSION}" STREQUAL "")
    Python_add_library(_mask MODULE "${GENERATED_C}" "${CMAKE_CURRENT_SOURCE_DIR}/common/maskApi.c" WITH_SOABI USE_SABI ${SKBUILD_SABI_VERSION})
else()
    Python_add_library(_mask MODULE "${GENERATED_C}" "${CMAKE_CURRENT_SOURCE_DIR}/common/maskApi.c" WITH_SOABI)
endif()

target_include_directories(
    _mask PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/common"
    ${Python_NumPy_INCLUDE_DIRS}
)

install(TARGETS _mask DESTINATION pycocotools)
