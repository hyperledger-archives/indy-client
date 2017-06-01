#!groovy

@Library('SovrinHelpers') _

def name = 'sovrin-client'

def testUbuntu = {
    try {
        echo 'Ubuntu Test: Checkout csm'
        checkout scm

        echo 'Ubuntu Test: Build docker image'
        def testEnv = dockerHelpers.build(name)

        testEnv.inside('--network host') {
            echo 'Ubuntu Test: Install dependencies'

            def sovrinCommon = helpers.extractVersion('sovrin-common')
            def sovrinNode = helpers.extractVersion('sovrin-node')
            def plenum = helpers.extractVersionOfSubdependency(sovrinCommon, 'plenum')
            testHelpers.install(deps: [plenum, sovrinNode])

            echo 'Ubuntu Test: Test'
            testHelpers.testRunner(resFile: "test-result.${NODE_NAME}.txt")
            //testHelpers.testJUnit(resFile: "test-result.${NODE_NAME}.xml")
        }
    }
    finally {
        echo 'Ubuntu Test: Cleanup'
        step([$class: 'WsCleanup'])
    }
}

def testWindows = {
    echo 'TODO: Implement me'
}

def testWindowsNoDocker = {
    try {
        echo 'Windows No Docker Test: Checkout csm'
        checkout scm

        testHelpers.createVirtualEnvAndExecute({ python, pip ->
            echo 'Windows No Docker Test: Install dependencies'
            def sovrinNode = helpers.extractVersion('sovrin-node')
            testHelpers.install(python: python, pip: pip, deps: [sovrinNode], isVEnv: true)

            echo 'Windows No Docker Test: Test'
            testHelpers.testJUnit(resFile: "test-result.${NODE_NAME}.xml", python: python)
        })
    }
    finally {
        echo 'Windows No Docker Test: Cleanup'
        step([$class: 'WsCleanup'])
    }
}

//testAndPublish(name, [ubuntu: testUbuntu, windows: testWindowsNoDocker, windowsNoDocker: testWindowsNoDocker])

options = new TestAndPublishOptions()
options.enable([StagesEnum.PACK_RELEASE_DEPS, StagesEnum.PACK_RELEASE_ST_DEPS])
testAndPublish(name, [ubuntu: testUbuntu], true, options)
