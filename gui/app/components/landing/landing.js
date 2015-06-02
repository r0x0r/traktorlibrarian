'use strict';

angular.module('librarian')
    .controller('LandingController', ['$scope', '$route', '$rootScope',
        function ($scope, $route, $rootScope) {
            console.log($rootScope.traktorDir);
    }]);