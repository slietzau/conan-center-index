from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class B2Conan(ConanFile):
    name = "b2"
    homepage = "https://www.bfgroup.xyz/b2/"
    description = "B2 makes it easy to build C++ projects, everywhere."
    topics = ("boost", "build")
    license = "BSL-1.0"
    settings = "os", "arch"
    url = "https://github.com/conan-io/conan-center-index"

    """
    * use_cxx_env: False, True

    Indicates if the build will use the CXX and
    CXXFLAGS environment variables. The common use is to add additional flags
    for building on specific platforms or for additional optimization options.

    * toolset: "auto", "cxx", "cross-cxx",
        "acc", "borland", "clang", "como", "gcc-nocygwin", "gcc",
        "intel-darwin", "intel-linux", "intel-win32", "kcc", "kylix",
        "mingw", "mipspro", "pathscale", "pgi", "qcc", "sun", "sunpro",
        "tru64cxx", "vacpp", "vc12", "vc14", "vc141", "vc142"

    Specifies the toolset to use for building. The default of "auto" detects
    a usable compiler for building and should be preferred. The "cxx" toolset
    uses the "CXX" and "CXXFLAGS" solely for building. Using the "cxx"
    toolset will also turn on the "use_cxx_env" option. And the "cross-cxx"
    toolset uses the "BUILD_CXX" and "BUILD_CXXFLAGS" vars. This frees the
    "CXX" and "CXXFLAGS" variables for use in subprocesses.
    """
    options = {
        "use_cxx_env": [False, True],
        "toolset": [
            "auto", "cxx", "cross-cxx",
            "acc", "borland", "clang", "como", "gcc-nocygwin", "gcc",
            "intel-darwin", "intel-linux", "intel-win32", "kcc", "kylix",
            "mingw", "mipspro", "pathscale", "pgi", "qcc", "sun", "sunpro",
            "tru64cxx", "vacpp", "vc12", "vc14", "vc141", "vc142"],
    }
    default_options = {
        "use_cxx_env": False,
        "toolset": "auto",
    }

    def configure(self):
        if (self.options.toolset == "cxx" or self.options.toolset == "cross-cxx") and not self.options.use_cxx_env:
            raise ConanInvalidConfiguration(
                "Option toolset 'cxx' and 'cross-cxx' requires 'use_cxx_env=True'")

    def package_id(self):
        del self.info.options.use_cxx_env
        del self.info.options.toolset

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination="source")

    def build(self):
        build_dir = os.path.join(self.source_folder, "source")
        engine_dir = os.path.join(build_dir, "src", "engine")
        with tools.chdir(engine_dir):
            with tools.environment_append({"VSCMD_START_DIR": os.curdir}):
                command = "build" if tools.os_info.is_windows else "./build.sh"
                if self.options.toolset != "auto":
                    command += " " + str(self.options.toolset)
                if self.options.use_cxx_env:
                    # Allow use of CXX env vars.
                    self.run(command)
                else:
                    # To avoid using the CXX env vars we clear them out for the build.
                    with tools.environment_append({"CXX": "", "CXXFLAGS": ""}):
                        self.run(command)
        with tools.chdir(build_dir):
            args = [
                os.path.join(engine_dir, "b2.exe" if tools.os_info.is_windows else "b2"),
                "--ignore-site-config",
                "--prefix=../output",
                "--abbreviate-paths",
            ]
            if self.options.toolset != "auto":
                args.append("toolset={}".format(self.options.toolset))
            args.append("install")
            self.run(" ".join(args))

    def package(self):
        self.copy("LICENSE.txt", src="source", dst="licenses")
        self.copy("*b2", src="output/bin", dst="bin")
        self.copy("*b2.exe", src="output/bin", dst="bin")
        self.copy("*.jam", src="output/share/boost-build", dst="bin/b2_src")

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]

        bin_path = [os.path.join(self.package_folder, "bin")]
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH = bin_path

        boost_build_path = os.path.join(self.package_folder, "bin", "b2_src", "src", "kernel")
        self.output.info("Setting BOOST_BUILD_PATH environment variable: {}".format(boost_build_path))
        self.env_info.BOOST_BUILD_PATH = boost_build_path
        self.user_info.boost_build_path = boost_build_path
