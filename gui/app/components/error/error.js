angular.module('librarian')
    .directive('error', [
        '$rootScope',

        function ($rootScope) {
          'use strict';

            return {
                scope: {
                    message: '='
                },
                restrict: 'E',
                templateUrl: '/static/components/error/error.html',
                link: function($scope) {
                    var processError = function(error, message) {
                        $scope.visible = true;
                        $scope.message = message;
                    };

                    $scope.closeError = function () {
                        $scope.visible = false;
                    }

                    $rootScope.$on('error', processError);
                }
            };
        }
    ]);
